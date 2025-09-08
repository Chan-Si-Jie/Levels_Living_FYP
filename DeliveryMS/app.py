import os, uuid, time, requests, json
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import mysql.connector
from mysql.connector import Error
import redis
from datetime import datetime, timedelta
import logging
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('mysql.connector').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Configuration class
class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'delivery-service-secret-key')
    
    # JWT Configuration (must match auth service)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']
    
    # Database Configuration
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_NAME = os.environ.get('DB_NAME', 'levels_living_db_new')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    
    # Redis Configuration
    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))
    
    # Service Configuration
    SERVICE_NAME = 'delivery-service'
    SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5004))

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for all routes
CORS(app, origins=["http://localhost:8000", "http://127.0.0.1:8000", "null"])

# Initialize JWT
jwt = JWTManager(app)

# Initialize Redis
try:
    redis_client = redis.Redis(
        host=Config.REDIS_HOST,
        port=Config.REDIS_PORT,
        db=Config.REDIS_DB,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )
    redis_client.ping()
    logger.info("Redis connected successfully")
except Exception as e:
    logger.error(f"Redis connection failed: {e}")
    redis_client = None

class DatabaseManager:
    def __init__(self):
        self.host = Config.DB_HOST
        self.database = Config.DB_NAME
        self.user = Config.DB_USER
        self.password = Config.DB_PASSWORD
        self.port = Config.DB_PORT
    
    def get_connection(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port,
                autocommit=True,
                connection_timeout=10
            )
            return connection
        except Error as e:
            logger.error(f"Database connection error: {e}")
            return None
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        connection = self.get_connection()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            else:
                return cursor.rowcount
        except Error as e:
            logger.error(f"Database query error: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

db = DatabaseManager()

# Initialize in-memory storage for compatibility
JOBS = {}
DRIVERS = {}

# Role-based access control decorator
def require_roles(*allowed_roles):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            
            if user_role not in allowed_roles:
                return jsonify({"error": "Insufficient permissions"}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 
ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
FIELD_MASK = (
    "routes.distanceMeters,"
    "routes.duration,"
    "routes.polyline.encodedPolyline,"
    "routes.optimizedIntermediateWaypointIndex"
)

# Allowed status values for deliveries (matching database schema)
VALID_STATUS = {
    "scheduled", "scheduled_adhoc", "assigned", "dispatched", "in_transit", 
    "arrived", "delivered", "failed", "rescheduled", "returned", "cancelled"
}

# Allowed status values for routes
VALID_ROUTE_STATUS = {"planned", "assigned", "in_progress", "completed", "cancelled"}

# === Utilities ===
def _err(msg, code=400):
    return jsonify({"error": msg}), code

def _get(d, *path):
    cur = d
    for p in path:
        if not isinstance(cur, dict) or p not in cur: return None
        cur = cur[p]
    return cur

def normalize_waypoint(w):
    """
    Accepts any of:
      - {"lat": 1.23, "lng": 4.56}
      - {"location":{"latLng":{"latitude":..,"longitude":..}}}
      - {"placeId":"..."}
      - "10 Bayfront Ave, Singapore"
    Returns Google Routes 'Waypoint' JSON.
    """
    if isinstance(w, dict) and "lat" in w and "lng" in w:
        return {"location": {"latLng": {"latitude": w["lat"], "longitude": w["lng"]}}}
    lat = _get(w, "location", "latLng", "latitude")
    lng = _get(w, "location", "latLng", "longitude")
    if lat is not None and lng is not None:
        return {"location": {"latLng": {"latitude": lat, "longitude": lng}}}
    if isinstance(w, dict) and "placeId" in w:
        return {"placeId": w["placeId"]}
    if isinstance(w, str):
        return {"location": {"address": w}}
    raise ValueError("Bad waypoint format")

def compute_route(origin, destination, stops):
    """Calls Google Routes API v2 with optimizeWaypointOrder=True."""
    if not GOOGLE_API_KEY:
        # JIC API Key not set in ENV
        raise RuntimeError("GOOGLE_API_KEY not set in environment.")

    body = {
        "origin": normalize_waypoint(origin),
        "destination": normalize_waypoint(destination or origin),
        "intermediates": [normalize_waypoint(s) for s in (stops or [])],
        "travelMode": "DRIVE",
        "routingPreference": "TRAFFIC_AWARE",
        "optimizeWaypointOrder": True,
    }
    r = requests.post(
        ROUTES_URL,
        headers={
            "X-Goog-Api-Key": GOOGLE_API_KEY,
            "X-Goog-FieldMask": FIELD_MASK
        },
        json=body,
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()
    # Basic guard
    if "routes" not in data or not data["routes"]:
        raise RuntimeError("No route returned from Google.")
    return data["routes"][0]

# === Error handler: return JSON instead of HTML debugger ===
@app.errorhandler(Exception)
def handle_any_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify({"error": str(e)}), code

# === Health ===
@app.get("/health")
def health():
    # Test database connection
    db_status = "connected" if db.get_connection() else "disconnected"
    
    # Test Redis connection
    redis_status = "connected"
    try:
        if redis_client:
            redis_client.ping()
    except:
        redis_status = "disconnected"
    
    return {
        "status": "ok",
        "service": Config.SERVICE_NAME,
        "database": db_status,
        "redis": redis_status,
        "time": int(time.time())
    }

# === Database helper functions ===
def save_job_to_db(job_data):
    """Save delivery job to database"""
    query = """
        INSERT INTO delivery_jobs (
            job_id, order_id, pickup_location, dropoff_location, stops, 
            driver_id, status, distance_meters, duration, polyline, 
            optimized_waypoint_index, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
    """
    
    params = (
        job_data.get("jobId"),
        job_data.get("orderId"),
        json.dumps(job_data.get("pickup")),
        json.dumps(job_data.get("dropoff")),
        json.dumps(job_data.get("stops", [])),
        job_data.get("driverId"),
        job_data.get("status"),
        job_data.get("route", {}).get("distanceMeters"),
        job_data.get("route", {}).get("duration"),
        job_data.get("route", {}).get("polyline"),
        json.dumps(job_data.get("route", {}).get("optimizedIntermediateWaypointIndex", []))
    )
    
    return db.execute_query(query, params)

def get_job_from_db(job_id):
    """Get delivery job from database"""
    query = "SELECT * FROM delivery_jobs WHERE job_id = %s"
    return db.execute_query(query, (job_id,), fetch_one=True)

def update_job_status_db(job_id, status):
    """Update job status in database"""
    query = "UPDATE delivery_jobs SET status = %s, updated_at = NOW() WHERE job_id = %s"
    return db.execute_query(query, (status, job_id))

def save_driver_to_db(driver_data):
    """Save driver to database"""
    query = """
        INSERT INTO drivers (driver_id, driver_name, vehicle, last_location, created_at, updated_at) 
        VALUES (%s, %s, %s, %s, NOW(), NOW())
        ON DUPLICATE KEY UPDATE 
        driver_name = VALUES(driver_name), 
        vehicle = VALUES(vehicle), 
        updated_at = NOW()
    """
    
    params = (
        driver_data.get("driverId"),
        driver_data.get("name"),
        driver_data.get("vehicle"),
        json.dumps(driver_data.get("last_location"))
    )
    
    return db.execute_query(query, params)

def update_driver_location_db(driver_id, location):
    """Update driver location in database"""
    query = "UPDATE drivers SET last_location = %s, updated_at = NOW() WHERE driver_id = %s"
    return db.execute_query(query, (json.dumps(location), driver_id))

def get_driver_from_db(driver_id):
    """Get driver from database"""
    query = "SELECT * FROM drivers WHERE driver_id = %s"
    return db.execute_query(query, (driver_id,), fetch_one=True)

# === Internal helper: route optimization (single-vehicle) ===
@app.post("/optimize-route")
def optimize_route():
    data = request.get_json(force=True)
    # accept either "stops" or "intermediates"
    stops = data.get("stops", data.get("intermediates", []))
    route = compute_route(data["origin"], data.get("destination", data["origin"]), stops)
    return jsonify({"routes": [route]})

# === Deliveries ===
@app.post("/deliveries")
def create_delivery():
    """
    Body:
    {
      "orderId": "ORD123",
      "pickup": { "lat": 1.36, "lng": 103.83 },        # origin
      "dropoff": { "lat": 1.44, "lng": 103.77 },       # destination
      "stops": [{ "lat": 1.4291, "lng": 103.8360 }],   # optional extra stops
      "driverId": "DRV88"                               # optional assignment
    }
    """
    data = request.get_json(force=True)
    order_id = data.get("orderId")
    if not order_id:
        return _err("orderId is required", 422)

    # Plan route immediately
    route = compute_route(data["pickup"], data.get("dropoff"), data.get("stops", []))

    job_id = str(uuid.uuid4())
    job = {
        "jobId": job_id,
        "orderId": order_id,
        "pickup": data["pickup"],
        "dropoff": data.get("dropoff", data["pickup"]),
        "stops": data.get("stops", []),
        "driverId": data.get("driverId"),
        "status": "planned",
        "route": {
            "distanceMeters": route.get("distanceMeters"),
            "duration": route.get("duration"),
            "polyline": route.get("polyline", {}).get("encodedPolyline"),
            "optimizedIntermediateWaypointIndex": route.get("optimizedIntermediateWaypointIndex", []),
        },
        "createdAt": int(time.time()),
        "updatedAt": int(time.time()),
    }
    
    # Save to both memory (for compatibility) and database
    JOBS[job_id] = job
    save_job_to_db(job)
    
    return jsonify(job), 201

@app.get("/deliveries/<job_id>")
def get_delivery(job_id):
    # Try memory first, then database
    job = JOBS.get(job_id)
    if not job:
        db_job = get_job_from_db(job_id)
        if db_job:
            # Convert database format back to API format
            job = {
                "jobId": db_job["job_id"],
                "orderId": db_job["order_id"],
                "pickup": json.loads(db_job["pickup_location"]) if db_job["pickup_location"] else None,
                "dropoff": json.loads(db_job["dropoff_location"]) if db_job["dropoff_location"] else None,
                "stops": json.loads(db_job["stops"]) if db_job["stops"] else [],
                "driverId": db_job["driver_id"],
                "status": db_job["status"],
                "route": {
                    "distanceMeters": db_job["distance_meters"],
                    "duration": db_job["duration"],
                    "polyline": db_job["polyline"],
                    "optimizedIntermediateWaypointIndex": json.loads(db_job["optimized_waypoint_index"]) if db_job["optimized_waypoint_index"] else []
                },
                "createdAt": int(db_job["created_at"].timestamp()) if db_job["created_at"] else None,
                "updatedAt": int(db_job["updated_at"].timestamp()) if db_job["updated_at"] else None
            }
    
    if not job:
        return _err("delivery not found", 404)
    return jsonify(job)

@app.patch("/deliveries/<job_id>/status")
def update_delivery_status(job_id):
    job = JOBS.get(job_id)
    if not job:
        return _err("delivery not found", 404)
    
    data = request.get_json(force=True)
    status = data.get("status")
    if status not in VALID_STATUS:
        return _err(f"invalid status. valid: {sorted(VALID_STATUS)}", 422)
    
    # Update both memory and database
    job["status"] = status
    job["updatedAt"] = int(time.time())
    update_job_status_db(job_id, status)
    
    return jsonify(job)

# === Tracking (customer-facing) ===
@app.get("/tracking/<job_id>")
def tracking(job_id):
    job = JOBS.get(job_id)
    if not job:
        return _err("delivery not found", 404)
    driver = DRIVERS.get(job.get("driverId")) if job.get("driverId") else None
    # Minimal view; hide internals
    view = {
        "jobId": job["jobId"],
        "orderId": job["orderId"],
        "status": job["status"],
        "eta": job["route"]["duration"],           # string like "1120s"
        "distanceMeters": job["route"]["distanceMeters"],
        "driver": None,
        "polyline": job["route"]["polyline"],      # let frontend draw path
    }
    if driver:
        view["driver"] = {
            "driverId": job["driverId"],
            "name": driver.get("name"),
            "location": driver.get("last_location"),  # {"lat":..,"lng":..}
        }
    return jsonify(view)

# === Drivers (minimal) === For now, assume that drivers are always available and can be assigned to jobs. Only one driver per day for now
@app.post("/drivers")
def create_driver():
    data = request.get_json(force=True)
    if "driverId" not in data:
        return _err("driverId is required", 422)
    driver_data = {
        "driverId": data["driverId"],
        "name": data.get("name"),
        "vehicle": data.get("vehicle"),
        "last_location": None,
        "createdAt": int(time.time()),
        "updatedAt": int(time.time()),
    }
    
    # Save to both memory and database
    DRIVERS[data["driverId"]] = driver_data
    save_driver_to_db(driver_data)
    
    return jsonify(driver_data), 201

@app.patch("/drivers/<driver_id>/location")
def update_driver_location(driver_id):
    d = DRIVERS.get(driver_id)
    if not d:
        return _err("driver not found", 404)
    
    data = request.get_json(force=True)
    if not isinstance(data.get("lat"), (int, float)) or not isinstance(data.get("lng"), (int, float)):
        return _err("lat and lng required (numbers)", 422)
    
    location = {"lat": data["lat"], "lng": data["lng"]}
    
    # Update both memory and database
    d["last_location"] = location
    d["updatedAt"] = int(time.time())
    update_driver_location_db(driver_id, location)
    
    return jsonify(d)

if __name__ == "__main__":
    port = int(os.getenv("SERVICE_PORT", 5004))
    app.run(host="0.0.0.0", port=port, debug=True)