import os, uuid, time, requests
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 
ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
FIELD_MASK = (
    "routes.distanceMeters,"
    "routes.duration,"
    "routes.polyline.encodedPolyline,"
    "routes.optimizedIntermediateWaypointIndex"
)

# === TODO:replace with either Shopify or Lark DB later ===
JOBS = {}       # jobId -> dict
DRIVERS = {}    # driverId -> dict (name, vehicle, last_location)
# Allowed status values for deliveries
VALID_STATUS = {"pending", "planned", "en_route", "delivered", "cancelled", "failed"}

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
    return {"status": "ok", "time": int(time.time())}

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
    JOBS[job_id] = job
    return jsonify(job), 201

@app.get("/deliveries/<job_id>")
def get_delivery(job_id):
    job = JOBS.get(job_id)
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
    job["status"] = status
    job["updatedAt"] = int(time.time())
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
    DRIVERS[data["driverId"]] = {
        "driverId": data["driverId"],
        "name": data.get("name"),
        "vehicle": data.get("vehicle"),
        "last_location": None,
        "createdAt": int(time.time()),
        "updatedAt": int(time.time()),
    }
    return jsonify(DRIVERS[data["driverId"]]), 201

@app.patch("/drivers/<driver_id>/location")
def update_driver_location(driver_id):
    d = DRIVERS.get(driver_id)
    if not d:
        return _err("driver not found", 404)
    data = request.get_json(force=True)
    if not isinstance(data.get("lat"), (int, float)) or not isinstance(data.get("lng"), (int, float)):
        return _err("lat and lng required (numbers)", 422)
    d["last_location"] = {"lat": data["lat"], "lng": data["lng"]}
    d["updatedAt"] = int(time.time())
    return jsonify(d)

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5004, debug=True)