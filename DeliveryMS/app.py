import os, uuid, time, requests
from flask import Flask, request, jsonify, render_template
from werkzeug.exceptions import HTTPException

app = Flask(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") 
ROUTES_URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
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

def get_warehouse_waypoint():
    lat = os.getenv("WAREHOUSE_LAT")
    long = os.getenv("WAREHOUSE_LONG")
    if lat and long:
        return {"location": {"latLng": {"latitude": float(lat), "longitude": float(long)}}}

    place_id = os.getenv("WAREHOUSE_PLACE_ID")
    if place_id:
        return {"placeId": place_id}

    addr = os.getenv("WAREHOUSE_ADDRESS")
    if addr:
        return {"location": {"address": addr}}

    raise RuntimeError("Warehouse not configured: set WAREHOUSE_LAT/LNG or WAREHOUSE_PLACE_ID or WAREHOUSE_ADDRESS in .env")


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



def geocode_address(address_or_postal: str):
    """Return {'lat': float, 'lng': float, 'formatted_address': str, 'place_id': str}."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set in environment (needed for Geocoding).")
    r = requests.get(GEOCODE_URL, params={"address": address_or_postal, "key": api_key}, timeout=10)
    r.raise_for_status()
    data = r.json()
    if data.get("status") != "OK" or not data.get("results"):
        msg = data.get("error_message") or data.get("status") or "geocode failed"
        raise RuntimeError(f"Geocode failed for '{address_or_postal}': {msg}")
    res = data["results"][0]
    loc = res["geometry"]["location"]
    return {"lat": float(loc["lat"]), "lng": float(loc["lng"]),
            "formatted_address": res.get("formatted_address"), "place_id": res.get("place_id")}

def to_latlng(value):
    """
    Accepts:
      - {"lat": 1.23, "lng": 4.56}
      - "10 Bayfront Ave, Singapore 018956"
      - "018956"  (postal)
    Returns dict: {"lat": float, "lng": float}
    """
    if isinstance(value, dict) and "lat" in value and "lng" in value:
        try:
            lat = float(value["lat"]); lng = float(value["lng"])
            return {"lat": lat, "lng": lng}
        except Exception:
            raise ValueError("lat/lng must be numeric.")
    if isinstance(value, str):
        g = geocode_address(value)
        return {"lat": g["lat"], "lng": g["lng"]}
    raise ValueError("Expected {lat,lng} or address string.")



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
      "pickup": { "lat": 1.375645, "lng": 103.929573 }, # origin, this is always going to be the tampines warehouse
      "dropoff": { "lat": 1.44, "lng": 103.77 },       # destination
      "stops": [{ "lat": 1.4291, "lng": 103.8360 }],   # optional extra stops
      "driverId": "DRV88"                               # optional assignment
    }
    """
    data = request.get_json(force=True)
    order_id = data.get("orderId")
    if not order_id:
        return _err("orderId is required", 422)

    # Warehouse as permanent origin (lat/lng)
    wh_lat = float(os.getenv("WAREHOUSE_LAT", "1.375645"))
    wh_lng = float(os.getenv("WAREHOUSE_LNG", "103.929573"))
    origin_latlng = {"lat": wh_lat, "lng": wh_lng}

    # Accept dropoff as address or {lat,lng}
    if "dropoff" not in data:
        return _err("dropoff is required (address string or {lat,lng})", 422)
    try:
        dropoff_latlng = to_latlng(data["dropoff"])
    except Exception as e:
        return _err(f"Invalid dropoff: {e}", 422)

    # Accept stops as addresses or {lat,lng}
    raw_stops = data.get("stops", [])
    stops_latlng = []
    try:
        for s in raw_stops:
            stops_latlng.append(to_latlng(s))
    except Exception as e:
        return _err(f"Invalid stop: {e}", 422)

    # Plan route (normalize_waypoint already supports both formats)
    route = compute_route(
        origin_latlng,                  # always warehouse
        dropoff_latlng,                 # resolved
        stops_latlng                    # resolved
    )

    job_id = str(uuid.uuid4())
    job = {
        "jobId": job_id,
        "orderId": order_id,
        "pickup": origin_latlng,               # always warehouse lat/lng for UI
        "dropoff": dropoff_latlng,             # resolved lat/lng
        "stops": stops_latlng,                 # resolved lat/lng list
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

    view = {
        "jobId": job["jobId"],
        "orderId": job["orderId"],
        "status": job["status"],
        "eta": job["route"]["duration"],           # string like "1120s"
        "distanceMeters": job["route"]["distanceMeters"],
        "driver": None,
        "polyline": job["route"]["polyline"],      # let frontend draw path
        "pickup": job["pickup"],
        "dropoff": job["dropoff"],
        "stops": job["stops"],
        "optimizedIntermediateWaypointIndex": job["route"].get("optimizedIntermediateWaypointIndex", []), #This is an array of indices indicating the new order of stops, we need this for relabelling the order of stops in the frontend
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

# Serve the testing page, injecting the browser key from env
@app.get("/testing")
def testing():
    # Guard: make 500s informative instead of cryptic
    js_key = os.getenv("GOOGLE_JS_KEY") or GOOGLE_API_KEY
    if not js_key:
        # Renders a small page explaining what's missing
        return render_template("testing.html", google_api_key=""), 200
    return render_template("testing.html", google_api_key=js_key)




if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)