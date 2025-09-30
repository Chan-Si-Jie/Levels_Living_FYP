# OrderMS/app.py
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
import uuid
import redis
import requests
import json
from datetime import datetime, timedelta
import logging
from functools import wraps
from typing import Dict, List, Optional, Any
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('mysql.connector').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Configuration class
class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'order-service-secret-key'

    # JWT Configuration (should match auth service)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']

    # Database Configuration
    DB_HOST = os.environ.get('DB_HOST') or 'localhost'
    DB_NAME = os.environ.get('DB_NAME') or 'levels_living_db_new'
    DB_USER = os.environ.get('DB_USER') or 'root'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or ''
    DB_PORT = int(os.environ.get('DB_PORT', 3306))

    # Redis Configuration
    REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
    REDIS_DB = int(os.environ.get('REDIS_DB', 0))

    # Service Configuration
    SERVICE_NAME = 'order-service'
    SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5005))

    # Microservice URLs
    USER_AUTH_SERVICE_URL = os.environ.get('USER_AUTH_SERVICE_URL') or 'http://localhost:5001'
    CUSTOMER_SERVICE_URL = os.environ.get('CUSTOMER_SERVICE_URL') or 'http://localhost:5002'
    INVENTORY_SERVICE_URL = os.environ.get('INVENTORY_SERVICE_URL') or 'http://localhost:5003'
    DELIVERY_SERVICE_URL = os.environ.get('DELIVERY_SERVICE_URL') or 'http://localhost:5004'

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for all routes
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize JWT
jwt = JWTManager(app)

# Initialize Redis connection
try:
    redis_client = redis.Redis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB'],
        decode_responses=True
    )
    redis_client.ping()
    logger.info("Redis connection established")
except Exception as e:
    logger.error(f"Redis connection failed: {e}")
    redis_client = None

# Database connection helper
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=app.config['DB_HOST'],
            database=app.config['DB_NAME'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD'],
            port=app.config['DB_PORT'],
            autocommit=True
        )
        return connection
    except Error as e:
        logger.error(f"Database connection error: {e}")
        return None

# Service Client Classes
class ServiceClient:
    def __init__(self, base_url: str, service_name: str):
        self.base_url = base_url.rstrip('/')
        self.service_name = service_name
        self.timeout = 10

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"{self.service_name} request failed: {e}")
            return None

    def get(self, endpoint: str, **kwargs) -> Optional[Dict]:
        return self._make_request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Optional[Dict]:
        return self._make_request('POST', endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> Optional[Dict]:
        return self._make_request('PUT', endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs) -> Optional[Dict]:
        return self._make_request('PATCH', endpoint, **kwargs)

# Initialize service clients
customer_service = ServiceClient(app.config['CUSTOMER_SERVICE_URL'], 'CustomerService')
inventory_service = ServiceClient(app.config['INVENTORY_SERVICE_URL'], 'InventoryService')
delivery_service = ServiceClient(app.config['DELIVERY_SERVICE_URL'], 'DeliveryService')
auth_service = ServiceClient(app.config['USER_AUTH_SERVICE_URL'], 'AuthService')

# JWT token blacklist check
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    if not redis_client:
        return False
    jti = jwt_payload['jti']
    return redis_client.get(f"blacklist:{jti}") is not None

# Auth decorator that checks with auth service
def auth_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

# Helper functions
def generate_order_number() -> str:
    """Generate unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d")
    random_suffix = str(uuid.uuid4())[:8].upper()
    return f"ORD-{timestamp}-{random_suffix}"

def validate_order_items(items: List[Dict]) -> tuple[bool, str, List[Dict]]:
    """Validate order items against inventory and return enriched item data"""
    if not items:
        return False, "Order must contain at least one item", []

    enriched_items = []
    total_value = 0

    with ThreadPoolExecutor(max_workers=5) as executor:
        # Fetch inventory data for all SKUs concurrently
        sku_futures = {
            executor.submit(inventory_service.get, f"/inventory/{item['sku']}"): item
            for item in items
        }

        for future in as_completed(sku_futures):
            item = sku_futures[future]
            inventory_data = future.result()

            if not inventory_data:
                return False, f"SKU {item['sku']} not found in inventory", []

            if not inventory_data.get('is_active', False):
                return False, f"SKU {item['sku']} is not active", []

            # Enrich item with inventory data
            enriched_item = {
                'sku': item['sku'],
                'quantity': item['quantity'],
                'item_name': inventory_data.get('item_name'),
                'variant': inventory_data.get('variant'),
                'unit_price': inventory_data.get('unit_price', 0),
                'delivery_type': inventory_data.get('delivery_type', 'standard'),
                'special_handling_required': inventory_data.get('special_handling_required', False),
                'assembly_required': inventory_data.get('assembly_required', False)
            }

            total_value += enriched_item['unit_price'] * enriched_item['quantity']
            enriched_items.append(enriched_item)

    return True, "", enriched_items

class OrderOrchestrator:
    """Main class for orchestrating order-related operations"""

    def __init__(self):
        self.db = get_db_connection()

    def create_order(self, customer_id: str, items: List[Dict], special_instructions: str = None) -> Dict:
        """Create a new order with full validation and service coordination"""
        try:
            # Step 1: Validate customer
            customer_data = customer_service.get(f"/customers/{customer_id}")
            if not customer_data:
                return {"error": "Customer not found", "status": 400}

            # Step 2: Validate and enrich order items
            valid, error_msg, enriched_items = validate_order_items(items)
            if not valid:
                return {"error": error_msg, "status": 400}

            # Step 3: Create order in database
            order_id = str(uuid.uuid4())
            order_no = generate_order_number()
            order_value = sum(item['unit_price'] * item['quantity'] for item in enriched_items)

            # Insert order
            cursor = self.db.cursor()
            order_query = """
                INSERT INTO orders (order_id, order_no, customer_id, status, order_date,
                                   order_value, note, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            now = datetime.now()
            cursor.execute(order_query, (
                order_id, order_no, customer_id, 'received', now.date(),
                order_value, special_instructions, now, now
            ))

            # Insert order items
            item_query = """
                INSERT INTO order_items (item_id, order_id, sku, item_name, variant,
                                       quantity, unit_price, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            for item in enriched_items:
                item_id = str(uuid.uuid4())
                cursor.execute(item_query, (
                    item_id, order_id, item['sku'], item['item_name'],
                    item['variant'], item['quantity'], item['unit_price'], now, now
                ))

            cursor.close()

            # Step 4: Create delivery job (if customer has delivery address)
            delivery_job_id = None
            if customer_data.get('latitude') and customer_data.get('longitude'):
                delivery_data = {
                    "orderId": order_no,
                    "pickup": {"lat": 1.3521, "lng": 103.8198},  # Default warehouse location
                    "dropoff": {
                        "lat": customer_data['latitude'],
                        "lng": customer_data['longitude']
                    }
                }

                delivery_response = delivery_service.post("/deliveries", json=delivery_data)
                if delivery_response:
                    delivery_job_id = delivery_response.get('jobId')

            # Step 5: Update order status to validated
            self.update_order_status(order_id, 'validated')

            # Return complete order data
            return {
                "order_id": order_id,
                "order_no": order_no,
                "customer_id": customer_id,
                "status": "validated",
                "order_value": order_value,
                "items": enriched_items,
                "delivery_job_id": delivery_job_id,
                "customer": customer_data,
                "created_at": now.isoformat()
            }

        except Exception as e:
            logger.error(f"Order creation failed: {e}")
            return {"error": "Internal server error", "status": 500}

    def get_order_details(self, order_id: str) -> Optional[Dict]:
        """Get comprehensive order details with aggregated data"""
        try:
            cursor = self.db.cursor(dictionary=True)

            # Get order data
            order_query = """
                SELECT o.*, c.customer_contact, c.customer_street, c.customer_unit,
                       c.customer_postal_code, c.latitude, c.longitude
                FROM orders o
                LEFT JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.order_id = %s
            """
            cursor.execute(order_query, (order_id,))
            order_data = cursor.fetchone()

            if not order_data:
                return None

            # Get order items
            items_query = """
                SELECT * FROM order_items WHERE order_id = %s
            """
            cursor.execute(items_query, (order_id,))
            items = cursor.fetchall()

            cursor.close()

            # Get delivery information if available
            delivery_info = None
            if order_data['order_no']:
                delivery_response = delivery_service.get(f"/tracking/{order_data['order_no']}")
                if delivery_response:
                    delivery_info = delivery_response

            return {
                "order": order_data,
                "items": items,
                "delivery": delivery_info
            }

        except Exception as e:
            logger.error(f"Failed to get order details: {e}")
            return None

    def update_order_status(self, order_id: str, status: str) -> bool:
        """Update order status"""
        try:
            cursor = self.db.cursor()
            query = "UPDATE orders SET status = %s, updated_at = %s WHERE order_id = %s"
            cursor.execute(query, (status, datetime.now(), order_id))
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Failed to update order status: {e}")
            return False

    def initiate_delivery(self, order_id: str) -> Dict:
        """Initiate delivery process for an order"""
        try:
            order_details = self.get_order_details(order_id)
            if not order_details:
                return {"error": "Order not found", "status": 404}

            order_data = order_details['order']

            if order_data['status'] not in ['validated', 'processing', 'ready_for_delivery']:
                return {"error": "Order not ready for delivery", "status": 400}

            # Create delivery if not exists
            if not order_details.get('delivery'):
                delivery_data = {
                    "orderId": order_data['order_no'],
                    "pickup": {"lat": 1.3521, "lng": 103.8198},
                    "dropoff": {
                        "lat": order_data['latitude'],
                        "lng": order_data['longitude']
                    }
                }

                delivery_response = delivery_service.post("/deliveries", json=delivery_data)
                if not delivery_response:
                    return {"error": "Failed to create delivery", "status": 500}

            # Update order status
            self.update_order_status(order_id, 'out_for_delivery')

            return {"message": "Delivery initiated successfully", "status": 200}

        except Exception as e:
            logger.error(f"Failed to initiate delivery: {e}")
            return {"error": "Internal server error", "status": 500}

# Initialize orchestrator
orchestrator = OrderOrchestrator()

# API Routes
@app.route('/health', methods=['GET'])
def health():
    db_status = "connected" if get_db_connection() else "disconnected"
    redis_status = "connected" if redis_client and redis_client.ping() else "disconnected"

    return jsonify({
        "service": app.config['SERVICE_NAME'],
        "status": "ok",
        "database": db_status,
        "redis": redis_status,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/orders', methods=['POST'])
@auth_required
def create_order():
    """Create a new order"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body required"}), 400

    customer_id = data.get('customer_id')
    items = data.get('items', [])
    special_instructions = data.get('special_instructions')

    if not customer_id:
        return jsonify({"error": "customer_id is required"}), 400

    if not items:
        return jsonify({"error": "items are required"}), 400

    result = orchestrator.create_order(customer_id, items, special_instructions)

    if "error" in result:
        return jsonify({"error": result["error"]}), result.get("status", 400)

    return jsonify(result), 201

@app.route('/orders/<order_id>', methods=['GET'])
@auth_required
def get_order(order_id):
    """Get order details"""
    order_details = orchestrator.get_order_details(order_id)

    if not order_details:
        return jsonify({"error": "Order not found"}), 404

    return jsonify(order_details)

@app.route('/orders/<order_id>/status', methods=['PUT'])
@auth_required
def update_order_status(order_id):
    """Update order status"""
    data = request.get_json()

    if not data or 'status' not in data:
        return jsonify({"error": "status is required"}), 400

    valid_statuses = [
        'received', 'validated', 'processing', 'in_assembly',
        'ready_for_delivery', 'out_for_delivery', 'delivered',
        'failed', 'cancelled', 'returned'
    ]

    if data['status'] not in valid_statuses:
        return jsonify({"error": f"Invalid status. Valid statuses: {valid_statuses}"}), 400

    success = orchestrator.update_order_status(order_id, data['status'])

    if not success:
        return jsonify({"error": "Failed to update order status"}), 500

    return jsonify({"message": "Order status updated successfully"})

@app.route('/orders/customer/<customer_id>', methods=['GET'])
@auth_required
def get_customer_orders(customer_id):
    """Get all orders for a customer"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT o.*, COUNT(oi.item_id) as item_count
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.customer_id = %s
            GROUP BY o.order_id
            ORDER BY o.created_at DESC
        """
        cursor.execute(query, (customer_id,))
        orders = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify({"orders": orders})

    except Exception as e:
        logger.error(f"Failed to get customer orders: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/orders/<order_id>/deliver', methods=['POST'])
@auth_required
def initiate_delivery(order_id):
    """Initiate delivery for an order"""
    result = orchestrator.initiate_delivery(order_id)

    if "error" in result:
        return jsonify({"error": result["error"]}), result.get("status", 400)

    return jsonify(result)

@app.route('/orders/<order_id>/tracking', methods=['GET'])
def get_order_tracking(order_id):
    """Get comprehensive order and delivery tracking (public endpoint)"""
    order_details = orchestrator.get_order_details(order_id)

    if not order_details:
        return jsonify({"error": "Order not found"}), 404

    # Return public-safe tracking information
    tracking_info = {
        "order_id": order_id,
        "order_no": order_details['order']['order_no'],
        "status": order_details['order']['status'],
        "order_date": order_details['order']['order_date'].isoformat() if order_details['order']['order_date'] else None,
        "items_count": len(order_details['items']),
        "delivery": order_details.get('delivery')
    }

    return jsonify(tracking_info)

# ============================================
# DELIVERY SCHEDULING ENDPOINTS
# ============================================

@app.route('/orders/unscheduled', methods=['GET'])
@auth_required
def get_unscheduled_orders():
    """
    Get all unscheduled orders ready for scheduling.
    Uses v_unscheduled_orders view which auto-sorts by priority.
    """
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor(dictionary=True)

        # Query the view that handles all the complex sorting
        query = """
            SELECT * FROM v_unscheduled_orders
        """
        cursor.execute(query)
        orders = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "count": len(orders),
            "orders": orders
        }), 200

    except Exception as e:
        logger.error(f"Error fetching unscheduled orders: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/orders/schedule', methods=['POST'])
@auth_required
def create_schedule():
    """
    Create a delivery schedule from selected orders.

    Expected payload:
    {
        "order_ids": ["order-id-1", "order-id-2", ...],
        "schedule_date": "2025-10-01",
        "driver_id": "DRV001",  // optional
        "team": "Team A"        // optional
    }
    """
    try:
        data = request.get_json()
        order_ids = data.get('order_ids', [])
        schedule_date = data.get('schedule_date')
        driver_id = data.get('driver_id')
        team = data.get('team')

        # Get current user from JWT
        current_user = get_jwt_identity()

        # Validation
        if not order_ids or len(order_ids) == 0:
            return jsonify({"error": "No orders selected"}), 400

        if not schedule_date:
            return jsonify({"error": "Schedule date is required"}), 400

        if len(order_ids) > 18:
            return jsonify({"error": "Cannot schedule more than 18 locations per day"}), 400

        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor(dictionary=True)

        # Step 1: Get order details with customer info, sorted by priority and postal code
        placeholders = ','.join(['%s'] * len(order_ids))
        query = f"""
            SELECT
                o.order_id,
                o.order_no,
                o.order_type,
                o.preferred_delivery_time,
                c.customer_id,
                c.customer_name,
                c.customer_postal_code,
                c.latitude,
                c.longitude,
                c.customer_street,
                c.customer_unit,
                CASE o.order_type
                    WHEN 'asap' THEN 1
                    WHEN 'adhoc' THEN 2
                    WHEN 'pre_order' THEN 3
                    WHEN 'custom_date' THEN 4
                    ELSE 5
                END as type_priority
            FROM orders o
            INNER JOIN customers c ON o.customer_id = c.customer_id
            WHERE o.order_id IN ({placeholders})
            AND o.is_scheduled = 0
            ORDER BY type_priority ASC, c.customer_postal_code ASC
        """

        cursor.execute(query, order_ids)
        orders = cursor.fetchall()

        if len(orders) != len(order_ids):
            cursor.close()
            connection.close()
            return jsonify({"error": "Some orders not found or already scheduled"}), 400

        # Step 2: Create delivery_schedule record
        schedule_id = str(uuid.uuid4())
        insert_schedule_query = """
            INSERT INTO delivery_schedules
            (schedule_id, schedule_date, driver_id, team, total_locations, status, created_by)
            VALUES (%s, %s, %s, %s, %s, 'draft', %s)
        """
        cursor.execute(insert_schedule_query, (
            schedule_id,
            schedule_date,
            driver_id,
            team,
            len(orders),
            current_user
        ))

        # Step 3: Create schedule_orders records with sequence numbers
        schedule_orders_data = []
        for idx, order in enumerate(orders, start=1):
            schedule_order_id = str(uuid.uuid4())
            schedule_orders_data.append((
                schedule_order_id,
                schedule_id,
                order['order_id'],
                idx,  # sequence_number
                order['customer_postal_code'],
                order['latitude'],
                order['longitude']
            ))

        insert_schedule_orders_query = """
            INSERT INTO schedule_orders
            (schedule_order_id, schedule_id, order_id, sequence_number,
             postal_code, latitude, longitude, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'scheduled')
        """
        cursor.executemany(insert_schedule_orders_query, schedule_orders_data)

        # Step 4: Update orders as scheduled
        update_orders_query = f"""
            UPDATE orders
            SET is_scheduled = 1,
                scheduled_delivery_date = %s,
                scheduled_by = %s,
                scheduled_at = NOW()
            WHERE order_id IN ({placeholders})
        """
        cursor.execute(update_orders_query, [schedule_date, current_user] + order_ids)

        # Step 5: Prepare waypoints for DeliveryMS (postal codes)
        # DeliveryMS will convert postal codes to lat/lng
        waypoints = [
            {
                "order_id": order['order_id'],
                "postal_code": order['customer_postal_code'],
                "sequence": idx
            }
            for idx, order in enumerate(orders, start=1)
        ]

        # Step 6: Call DeliveryMS to optimize route
        delivery_service = ServiceClient(app.config['DELIVERY_SERVICE_URL'], 'delivery-service')
        route_response = delivery_service.post('/optimize-route', json={
            "waypoints": waypoints,
            "schedule_date": schedule_date
        })

        route_data = {}
        if route_response and route_response.get('success'):
            route_data = route_response.get('route', {})

            # Update schedule with route data
            update_schedule_query = """
                UPDATE delivery_schedules
                SET route_polyline = %s,
                    total_distance_meters = %s,
                    total_duration_seconds = %s,
                    estimated_end_time = %s
                WHERE schedule_id = %s
            """
            cursor.execute(update_schedule_query, (
                route_data.get('polyline'),
                route_data.get('distance_meters'),
                route_data.get('duration_seconds'),
                route_data.get('estimated_end_time'),
                schedule_id
            ))

        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Schedule created successfully",
            "schedule_id": schedule_id,
            "schedule_date": schedule_date,
            "total_locations": len(orders),
            "orders": [
                {
                    "order_no": order['order_no'],
                    "sequence": idx,
                    "customer": order['customer_name'],
                    "postal_code": order['customer_postal_code']
                }
                for idx, order in enumerate(orders, start=1)
            ],
            "route": route_data
        }), 201

    except Exception as e:
        logger.error(f"Error creating schedule: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/schedules/<schedule_date>', methods=['GET'])
@auth_required
def get_schedule_by_date(schedule_date):
    """
    Get all scheduled deliveries for a specific date.
    Uses v_scheduled_deliveries view.
    """
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT * FROM v_scheduled_deliveries
            WHERE schedule_date = %s
            ORDER BY sequence_number ASC
        """
        cursor.execute(query, (schedule_date,))
        deliveries = cursor.fetchall()

        cursor.close()
        connection.close()

        # Group by schedule_id
        schedules = {}
        for delivery in deliveries:
            schedule_id = delivery['schedule_id']
            if schedule_id not in schedules:
                schedules[schedule_id] = {
                    "schedule_id": schedule_id,
                    "schedule_date": delivery['schedule_date'],
                    "driver_id": delivery['driver_id'],
                    "driver_name": delivery['driver_name'],
                    "driver_contact": delivery['driver_contact'],
                    "team": delivery['team'],
                    "total_locations": delivery['total_locations'],
                    "max_locations": delivery['max_locations'],
                    "remaining_capacity": delivery['remaining_capacity'],
                    "status": delivery['schedule_status'],
                    "start_time": str(delivery['start_time']) if delivery['start_time'] else None,
                    "estimated_end_time": str(delivery['estimated_end_time']) if delivery['estimated_end_time'] else None,
                    "route_polyline": delivery['route_polyline'],
                    "deliveries": []
                }

            schedules[schedule_id]['deliveries'].append({
                "sequence": delivery['sequence_number'],
                "order_no": delivery['order_no'],
                "order_type": delivery['order_type'],
                "customer_name": delivery['customer_name'],
                "customer_contact": delivery['customer_contact'],
                "postal_code": delivery['customer_postal_code'],
                "address": f"{delivery['customer_street']} {delivery['customer_unit']}".strip(),
                "housing_type": delivery['housing_type'],
                "total_items": delivery['total_items'],
                "estimated_arrival": str(delivery['estimated_arrival_time']) if delivery['estimated_arrival_time'] else None,
                "actual_arrival": str(delivery['actual_arrival_time']) if delivery['actual_arrival_time'] else None,
                "status": delivery['delivery_status'],
                "requires_warehouse_return": bool(delivery['requires_warehouse_return']),
                "latitude": float(delivery['latitude']) if delivery['latitude'] else None,
                "longitude": float(delivery['longitude']) if delivery['longitude'] else None
            })

        return jsonify({
            "success": True,
            "schedule_date": schedule_date,
            "schedules": list(schedules.values())
        }), 200

    except Exception as e:
        logger.error(f"Error fetching schedule: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/orders/<order_id>/complete', methods=['PATCH'])
@auth_required
def mark_delivery_complete(order_id):
    """
    Mark an order's delivery as completed.
    Updates both order status and delivery_completed flag.
    """
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500

        cursor = connection.cursor(dictionary=True)

        # Check if order exists
        cursor.execute("SELECT order_id, order_no, status FROM orders WHERE order_id = %s", (order_id,))
        order = cursor.fetchone()

        if not order:
            cursor.close()
            connection.close()
            return jsonify({"error": "Order not found"}), 404

        # Update order
        update_query = """
            UPDATE orders
            SET delivery_completed = 1,
                status = 'delivered',
                updated_at = NOW()
            WHERE order_id = %s
        """
        cursor.execute(update_query, (order_id,))

        # Also update schedule_orders status if exists
        update_schedule_query = """
            UPDATE schedule_orders
            SET status = 'delivered',
                actual_arrival_time = NOW()
            WHERE order_id = %s
        """
        cursor.execute(update_schedule_query, (order_id,))

        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "message": "Delivery marked as complete",
            "order_id": order_id,
            "order_no": order['order_no']
        }), 200

    except Exception as e:
        logger.error(f"Error marking delivery complete: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/schedules/<schedule_id>', methods=['DELETE'])
@auth_required
def delete_schedule(schedule_id):
    """Delete/unschedule a delivery schedule and reset all orders"""
    try:
        cursor = get_db_cursor()

        # Check if schedule exists
        cursor.execute(
            "SELECT schedule_id, schedule_date, status FROM delivery_schedules WHERE schedule_id = %s",
            (schedule_id,)
        )
        schedule = cursor.fetchone()

        if not schedule:
            return jsonify({"error": "Schedule not found"}), 404

        # Get all orders in this schedule
        cursor.execute("""
            SELECT o.order_id, o.order_no
            FROM orders o
            JOIN schedule_orders so ON o.order_id = so.order_id
            WHERE so.schedule_id = %s
        """, (schedule_id,))
        orders = cursor.fetchall()

        # Reset all orders back to unscheduled
        cursor.execute("""
            UPDATE orders
            SET is_scheduled = 0,
                scheduled_delivery_date = NULL,
                scheduled_by = NULL,
                scheduled_at = NULL
            WHERE order_id IN (
                SELECT order_id FROM schedule_orders WHERE schedule_id = %s
            )
        """, (schedule_id,))

        # Delete schedule_orders entries
        cursor.execute("DELETE FROM schedule_orders WHERE schedule_id = %s", (schedule_id,))

        # Delete the schedule
        cursor.execute("DELETE FROM delivery_schedules WHERE schedule_id = %s", (schedule_id,))

        db.commit()

        logger.info(f"Schedule {schedule_id} deleted, {len(orders)} orders unscheduled")

        return jsonify({
            "success": True,
            "message": f"Schedule deleted successfully",
            "schedule_id": schedule_id,
            "orders_unscheduled": len(orders)
        }), 200

    except Exception as e:
        logger.error(f"Error deleting schedule: {e}")
        db.rollback()
        return jsonify({"error": str(e)}), 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.getenv("SERVICE_PORT", 5005))
    debug = os.getenv("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)