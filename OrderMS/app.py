# OrderMS/app.py - Order Management Service for Delivery Management
import os, uuid, time, requests
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
import mysql.connector
from mysql.connector import Error
import redis
from datetime import datetime, timedelta, date
import logging
import json
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('mysql.connector').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Configuration class
class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'order-management-secret-key')
    
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
    SERVICE_NAME = 'order-management-service'
    SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5005))
    
    # External Services
    CUSTOMER_SERVICE_URL = os.environ.get('CUSTOMER_SERVICE_URL', 'http://customer-service:5002')
    INVENTORY_SERVICE_URL = os.environ.get('INVENTORY_SERVICE_URL', 'http://inventory-service:5003')
    DELIVERY_SERVICE_URL = os.environ.get('DELIVERY_SERVICE_URL', 'http://delivery-service:5004')

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

# Utilities
def _err(msg, code=400):
    return jsonify({"error": msg}), code

def _success(data, message="Success", code=200):
    return jsonify({"message": message, "data": data}), code

# Valid order statuses for delivery management
VALID_ORDER_STATUS = {
    'received', 'ready_for_delivery', 'assigned_for_delivery', 
    'out_for_delivery', 'delivered', 'failed', 'cancelled', 'returned'
}

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

# === Order Management ===

@app.post("/orders")
@require_roles('admin', 'hq')
def create_order():
    """
    Create order for delivery management (items pre-assembled)
    Body:
    {
      "order_no": "ORD001",
      "shopify_order_id": "12345",
      "customer_contact": "+6591234567",
      "items": [
        {"sku": "SKU001", "quantity": 2, "unit_price": 199.00}
      ],
      "delivery_date": "2025-01-15",
      "special_delivery": false,
      "note": "Handle with care"
    }
    """
    data = request.get_json(force=True)
    
    # Validate required fields
    required_fields = ['order_no', 'customer_contact', 'items']
    for field in required_fields:
        if not data.get(field):
            return _err(f"{field} is required", 422)
    
    # Validate customer via CustomerMS
    try:
        customer_response = requests.get(
            f"{Config.CUSTOMER_SERVICE_URL}/customers/contact/{data['customer_contact']}"
        )
        if customer_response.status_code != 200:
            return _err("Customer not found", 404)
        customer = customer_response.json()
    except Exception as e:
        logger.error(f"Customer service error: {e}")
        return _err("Failed to validate customer", 500)
    
    # Create order
    order_id = str(uuid.uuid4())
    order_date = date.today()
    
    # Calculate total order value
    total_value = sum(item.get('quantity', 1) * item.get('unit_price', 0) for item in data['items'])
    
    order_query = """
        INSERT INTO orders (
            order_id, order_no, shopify_order_id, customer_id, status,
            order_date, order_value, special_delivery, note, delivery_date,
            source_system, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
    """
    
    order_params = (
        order_id,
        data['order_no'],
        data.get('shopify_order_id'),
        customer['customer_id'],
        'ready_for_delivery',  # Items are pre-assembled
        order_date,
        total_value,
        data.get('special_delivery', False),
        data.get('note'),
        data.get('delivery_date'),
        'manual'
    )
    
    result = db.execute_query(order_query, order_params)
    if result is None:
        return _err("Failed to create order", 500)
    
    # Add order items
    for item in data['items']:
        item_id = str(uuid.uuid4())
        item_query = """
            INSERT INTO order_items (
                item_id, order_id, sku, item_name, quantity, 
                unit_price, total_price, ready_for_delivery
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
        """
        
        item_params = (
            item_id,
            order_id,
            item['sku'],
            item.get('item_name', item['sku']),
            item['quantity'],
            item['unit_price'],
            item['quantity'] * item['unit_price']
        )
        
        db.execute_query(item_query, item_params)
    
    # Return created order
    order = {
        "order_id": order_id,
        "order_no": data['order_no'],
        "customer_contact": data['customer_contact'],
        "status": "ready_for_delivery",
        "order_date": str(order_date),
        "order_value": total_value,
        "items": data['items'],
        "created_at": int(time.time())
    }
    
    return _success(order, "Order created successfully", 201)

@app.get("/orders")
@require_roles('admin', 'hq', 'driver')
def get_orders():
    """Get orders for delivery management with filters"""
    status = request.args.get('status')
    driver_id = request.args.get('driver_id')
    delivery_date = request.args.get('delivery_date')
    
    query = """
        SELECT o.*, c.customer_contact, c.customer_street, c.customer_postal_code,
               dr.driver_name, COUNT(oi.item_id) as item_count
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        LEFT JOIN drivers dr ON o.assigned_driver_id = dr.driver_id
        LEFT JOIN order_items oi ON o.order_id = oi.order_id
        WHERE 1=1
    """
    params = []
    
    if status:
        query += " AND o.status = %s"
        params.append(status)
    
    if driver_id:
        query += " AND o.assigned_driver_id = %s"
        params.append(driver_id)
    
    if delivery_date:
        query += " AND o.delivery_date = %s"
        params.append(delivery_date)
    
    query += " GROUP BY o.order_id ORDER BY o.created_at DESC"
    
    orders = db.execute_query(query, params, fetch_all=True)
    
    if orders is None:
        return _err("Failed to fetch orders", 500)
    
    return _success(orders, "Orders retrieved successfully")

@app.get("/orders/<order_id>")
@require_roles('admin', 'hq', 'driver')
def get_order(order_id):
    """Get detailed order information"""
    query = """
        SELECT o.*, c.customer_contact, c.customer_street, c.customer_unit,
               c.customer_postal_code, c.housing_type, c.latitude, c.longitude,
               dr.driver_name, dr.driver_contact
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        LEFT JOIN drivers dr ON o.assigned_driver_id = dr.driver_id
        WHERE o.order_id = %s
    """
    
    order = db.execute_query(query, (order_id,), fetch_one=True)
    if not order:
        return _err("Order not found", 404)
    
    # Get order items
    items_query = "SELECT * FROM order_items WHERE order_id = %s"
    items = db.execute_query(items_query, (order_id,), fetch_all=True)
    
    order['items'] = items or []
    
    return _success(order, "Order retrieved successfully")

@app.patch("/orders/<order_id>/assign")
@require_roles('admin', 'hq')
def assign_order_for_delivery(order_id):
    """Assign order to driver for delivery"""
    data = request.get_json(force=True)
    driver_id = data.get('driver_id')
    delivery_date = data.get('delivery_date')
    time_slot = data.get('time_slot')
    
    if not driver_id or not delivery_date:
        return _err("driver_id and delivery_date are required", 422)
    
    # Update order
    update_query = """
        UPDATE orders 
        SET assigned_driver_id = %s, delivery_date = %s, 
            status = 'assigned_for_delivery', updated_at = NOW()
        WHERE order_id = %s
    """
    
    result = db.execute_query(update_query, (driver_id, delivery_date, order_id))
    if result == 0:
        return _err("Order not found", 404)
    
    # Create delivery assignment record
    assignment_id = str(uuid.uuid4())
    user_id = get_jwt_identity()
    
    assignment_query = """
        INSERT INTO delivery_assignments (
            assignment_id, order_id, driver_id, delivery_date, 
            time_slot, assigned_by, special_instructions
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    db.execute_query(assignment_query, (
        assignment_id, order_id, driver_id, delivery_date, 
        time_slot, user_id, data.get('special_instructions')
    ))
    
    # Create delivery job in DeliveryMS
    try:
        # Get order details for delivery creation
        order = db.execute_query(
            "SELECT o.*, c.latitude, c.longitude FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.order_id = %s",
            (order_id,), fetch_one=True
        )
        
        delivery_payload = {
            "orderId": order['order_no'],
            "pickup": {"lat": 1.3521, "lng": 103.8198},  # Default warehouse location
            "dropoff": {"lat": float(order['latitude']), "lng": float(order['longitude'])},
            "driverId": driver_id
        }
        
        delivery_response = requests.post(f"{Config.DELIVERY_SERVICE_URL}/deliveries", json=delivery_payload)
        if delivery_response.status_code not in [200, 201]:
            logger.error(f"Delivery service error: {delivery_response.status_code} - {delivery_response.text}")
            return _err("Failed to create delivery job", 500)
        logger.info(f"Delivery job created successfully for order {order['order_no']}")
    except Exception as e:
        logger.error(f"Failed to create delivery job: {e}")
        return _err("Failed to create delivery job", 500)
    
    return _success({"assignment_id": assignment_id}, "Order assigned for delivery successfully")

@app.patch("/orders/<order_id>/status")
@require_roles('admin', 'hq', 'driver')
def update_order_status(order_id):
    """Update order delivery status"""
    data = request.get_json(force=True)
    status = data.get('status')
    
    if status not in VALID_ORDER_STATUS:
        return _err(f"Invalid status. Valid: {sorted(VALID_ORDER_STATUS)}", 422)
    
    update_query = "UPDATE orders SET status = %s, updated_at = NOW() WHERE order_id = %s"
    result = db.execute_query(update_query, (status, order_id))
    
    if result == 0:
        return _err("Order not found", 404)
    
    # Update delivery assignment if exists
    if status in ['completed', 'failed']:
        assignment_status = 'completed' if status == 'delivered' else 'failed'
        db.execute_query(
            "UPDATE delivery_assignments SET status = %s WHERE order_id = %s",
            (assignment_status, order_id)
        )
    
    return _success({"order_id": order_id, "status": status}, "Order status updated successfully")

# === Dashboard & Reporting ===

@app.get("/dashboard")
@require_roles('admin', 'hq')
def get_dashboard():
    """Get HQ dashboard overview"""
    
    # Order status counts
    status_query = """
        SELECT status, COUNT(*) as count 
        FROM orders 
        WHERE DATE(created_at) >= DATE_SUB(CURDATE(), INTERVAL 7 DAYS)
        GROUP BY status
    """
    status_counts = db.execute_query(status_query, fetch_all=True)
    
    # Today's deliveries
    today_query = """
        SELECT o.order_no, c.customer_contact, dr.driver_name, o.status
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        LEFT JOIN drivers dr ON o.assigned_driver_id = dr.driver_id
        WHERE o.delivery_date = CURDATE()
        ORDER BY o.created_at DESC
        LIMIT 10
    """
    todays_deliveries = db.execute_query(today_query, fetch_all=True)
    
    # Driver utilization
    driver_query = """
        SELECT dr.driver_name, COUNT(o.order_id) as assigned_orders
        FROM drivers dr
        LEFT JOIN orders o ON dr.driver_id = o.assigned_driver_id 
            AND o.delivery_date = CURDATE()
        WHERE dr.is_active = TRUE
        GROUP BY dr.driver_id
    """
    driver_stats = db.execute_query(driver_query, fetch_all=True)
    
    dashboard_data = {
        "status_counts": status_counts or [],
        "todays_deliveries": todays_deliveries or [],
        "driver_utilization": driver_stats or [],
        "generated_at": int(time.time())
    }
    
    return _success(dashboard_data, "Dashboard data retrieved successfully")

# ===============================
# PROXY ENDPOINTS - OrderMS as Central Gateway
# All frontend calls go through OrderMS, which forwards to other microservices
# ===============================

# === Customer Management Proxy ===
@app.post("/customers")
@require_roles('admin', 'hq', 'customer_service')
def create_customer_proxy():
    """OrderMS proxy: Create customer via CustomerMS"""
    data = request.get_json(force=True)
    
    try:
        headers = {'Authorization': request.headers.get('Authorization')}
        response = requests.post(f"{Config.CUSTOMER_SERVICE_URL}/customers", json=data, headers=headers)
        
        logger.info(f"CustomerMS response: {response.status_code}")
        
        if response.status_code == 201:
            return _success(response.json(), "Customer created via OrderMS gateway", 201)
        else:
            return _err(f"CustomerMS error: {response.text}", response.status_code)
            
    except Exception as e:
        logger.error(f"CustomerMS proxy error: {e}")
        return _err("Failed to reach CustomerMS", 500)

@app.get("/customers")
@require_roles('admin', 'hq', 'customer_service')
def get_customers_proxy():
    """OrderMS proxy: Get all customers via CustomerMS"""
    try:
        headers = {'Authorization': request.headers.get('Authorization')}
        response = requests.get(f"{Config.CUSTOMER_SERVICE_URL}/customers", headers=headers)
        
        logger.info(f"CustomerMS response: {response.status_code}")
        
        if response.status_code == 200:
            return _success(response.json(), "Customers retrieved via OrderMS gateway")
        else:
            return _err(f"CustomerMS error: {response.text}", response.status_code)
            
    except Exception as e:
        logger.error(f"CustomerMS proxy error: {e}")
        return _err("Failed to reach CustomerMS", 500)

@app.get("/customers/<customer_id>")
@require_roles('admin', 'hq', 'customer_service')
def get_customer_by_id_proxy(customer_id):
    """OrderMS proxy: Get customer by ID via CustomerMS"""
    try:
        headers = {'Authorization': request.headers.get('Authorization')}
        response = requests.get(f"{Config.CUSTOMER_SERVICE_URL}/customers/{customer_id}", headers=headers)
        
        logger.info(f"CustomerMS response: {response.status_code}")
        
        if response.status_code == 200:
            return _success(response.json(), "Customer retrieved via OrderMS gateway")
        else:
            return _err(f"CustomerMS error: {response.text}", response.status_code)
            
    except Exception as e:
        logger.error(f"CustomerMS proxy error: {e}")
        return _err("Failed to reach CustomerMS", 500)

@app.get("/customers/contact/<contact>")
@require_roles('admin', 'hq', 'customer_service')
def get_customer_by_contact_proxy(contact):
    """OrderMS proxy: Get customer by contact via CustomerMS"""
    try:
        headers = {'Authorization': request.headers.get('Authorization')}
        response = requests.get(f"{Config.CUSTOMER_SERVICE_URL}/customers/contact/{contact}", headers=headers)
        
        logger.info(f"CustomerMS response: {response.status_code}")
        
        if response.status_code == 200:
            return _success(response.json(), "Customer retrieved via OrderMS gateway")
        else:
            return _err(f"CustomerMS error: {response.text}", response.status_code)
            
    except Exception as e:
        logger.error(f"CustomerMS proxy error: {e}")
        return _err("Failed to reach CustomerMS", 500)

@app.post("/customers/validate")
@require_roles('admin', 'hq', 'customer_service')
def validate_customer_proxy():
    """OrderMS proxy: Validate customer data via CustomerMS"""
    data = request.get_json(force=True)
    
    try:
        headers = {'Authorization': request.headers.get('Authorization')}
        response = requests.post(f"{Config.CUSTOMER_SERVICE_URL}/customers/validate", json=data, headers=headers)
        
        logger.info(f"CustomerMS response: {response.status_code}")
        
        if response.status_code == 200:
            return _success(response.json(), "Customer validated via OrderMS gateway")
        else:
            return _err(f"CustomerMS error: {response.text}", response.status_code)
            
    except Exception as e:
        logger.error(f"CustomerMS proxy error: {e}")
        return _err("Failed to reach CustomerMS", 500)

# === Inventory Management Proxy ===
@app.post("/inventory/products")
@require_roles('admin', 'hq')
def create_product_proxy():
    """OrderMS proxy: Create product via InventoryMS"""
    data = request.get_json(force=True)
    
    try:
        headers = {'Authorization': request.headers.get('Authorization')}
        response = requests.post(f"{Config.INVENTORY_SERVICE_URL}/inventory/products", json=data, headers=headers)
        
        logger.info(f"InventoryMS response: {response.status_code}")
        
        if response.status_code == 201:
            return _success(response.json(), "Product created via OrderMS gateway", 201)
        else:
            return _err(f"InventoryMS error: {response.text}", response.status_code)
            
    except Exception as e:
        logger.error(f"InventoryMS proxy error: {e}")
        return _err("Failed to reach InventoryMS", 500)

@app.get("/inventory/products")
@require_roles('admin', 'hq', 'warehouse')
def get_products_proxy():
    """OrderMS proxy: Get products via InventoryMS"""
    # Forward query parameters
    params = request.args.to_dict()
    
    try:
        headers = {'Authorization': request.headers.get('Authorization')}
        response = requests.get(f"{Config.INVENTORY_SERVICE_URL}/inventory/products", params=params, headers=headers)
        
        logger.info(f"InventoryMS response: {response.status_code}")
        
        if response.status_code == 200:
            return _success(response.json(), "Products retrieved via OrderMS gateway")
        else:
            return _err(f"InventoryMS error: {response.text}", response.status_code)
            
    except Exception as e:
        logger.error(f"InventoryMS proxy error: {e}")
        return _err("Failed to reach InventoryMS", 500)

@app.get("/inventory/products/<sku>")
@require_roles('admin', 'hq', 'warehouse')
def get_product_by_sku_proxy(sku):
    """OrderMS proxy: Get product by SKU via InventoryMS"""
    try:
        headers = {'Authorization': request.headers.get('Authorization')}
        response = requests.get(f"{Config.INVENTORY_SERVICE_URL}/inventory/products/{sku}", headers=headers)
        
        logger.info(f"InventoryMS response: {response.status_code}")
        
        if response.status_code == 200:
            return _success(response.json(), "Product retrieved via OrderMS gateway")
        else:
            return _err(f"InventoryMS error: {response.text}", response.status_code)
            
    except Exception as e:
        logger.error(f"InventoryMS proxy error: {e}")
        return _err("Failed to reach InventoryMS", 500)

@app.get("/inventory/delivery-types")
@require_roles('admin', 'hq', 'warehouse')
def get_delivery_types_proxy():
    """OrderMS proxy: Get delivery types via InventoryMS"""
    try:
        headers = {'Authorization': request.headers.get('Authorization')}
        response = requests.get(f"{Config.INVENTORY_SERVICE_URL}/inventory/delivery-types", headers=headers)
        
        logger.info(f"InventoryMS response: {response.status_code}")
        
        if response.status_code == 200:
            return _success(response.json(), "Delivery types retrieved via OrderMS gateway")
        else:
            return _err(f"InventoryMS error: {response.text}", response.status_code)
            
    except Exception as e:
        logger.error(f"InventoryMS proxy error: {e}")
        return _err("Failed to reach InventoryMS", 500)

@app.post("/inventory/delivery-requirements")
@require_roles('admin', 'hq', 'warehouse')
def get_delivery_requirements_proxy():
    """OrderMS proxy: Get delivery requirements via InventoryMS"""
    data = request.get_json(force=True)
    
    try:
        headers = {'Authorization': request.headers.get('Authorization')}
        response = requests.post(f"{Config.INVENTORY_SERVICE_URL}/inventory/delivery-requirements", json=data, headers=headers)
        
        logger.info(f"InventoryMS response: {response.status_code}")
        
        if response.status_code == 200:
            return _success(response.json(), "Delivery requirements retrieved via OrderMS gateway")
        else:
            return _err(f"InventoryMS error: {response.text}", response.status_code)
            
    except Exception as e:
        logger.error(f"InventoryMS proxy error: {e}")
        return _err("Failed to reach InventoryMS", 500)

# === Delivery Management Proxy ===
@app.get("/deliveries/<job_id>")
@require_roles('admin', 'hq', 'driver')
def get_delivery_job_proxy(job_id):
    """OrderMS proxy: Get delivery job via DeliveryMS"""
    try:
        response = requests.get(f"{Config.DELIVERY_SERVICE_URL}/deliveries/{job_id}")
        
        logger.info(f"DeliveryMS response: {response.status_code}")
        
        if response.status_code == 200:
            return _success(response.json(), "Delivery job retrieved via OrderMS gateway")
        else:
            return _err(f"DeliveryMS error: {response.text}", response.status_code)
            
    except Exception as e:
        logger.error(f"DeliveryMS proxy error: {e}")
        return _err("Failed to reach DeliveryMS", 500)

@app.get("/tracking/<job_id>")
def get_delivery_tracking_proxy(job_id):
    """OrderMS proxy: Get delivery tracking via DeliveryMS (public endpoint)"""
    try:
        response = requests.get(f"{Config.DELIVERY_SERVICE_URL}/tracking/{job_id}")
        
        logger.info(f"DeliveryMS response: {response.status_code}")
        
        if response.status_code == 200:
            return _success(response.json(), "Delivery tracking retrieved via OrderMS gateway")
        else:
            return _err(f"DeliveryMS error: {response.text}", response.status_code)
            
    except Exception as e:
        logger.error(f"DeliveryMS proxy error: {e}")
        return _err("Failed to reach DeliveryMS", 500)

@app.patch("/deliveries/<job_id>/status")
@require_roles('admin', 'hq', 'driver')
def update_delivery_status_proxy(job_id):
    """OrderMS proxy: Update delivery status via DeliveryMS"""
    data = request.get_json(force=True)
    
    try:
        response = requests.patch(f"{Config.DELIVERY_SERVICE_URL}/deliveries/{job_id}/status", json=data)
        
        logger.info(f"DeliveryMS response: {response.status_code}")
        
        if response.status_code == 200:
            return _success(response.json(), "Delivery status updated via OrderMS gateway")
        else:
            return _err(f"DeliveryMS error: {response.text}", response.status_code)
            
    except Exception as e:
        logger.error(f"DeliveryMS proxy error: {e}")
        return _err("Failed to reach DeliveryMS", 500)

# === Service Health Proxy ===
@app.get("/services/health")
def get_all_services_health():
    """OrderMS gateway: Get health status of all microservices"""
    services = {}
    
    try:
        # Check CustomerMS
        response = requests.get(f"{Config.CUSTOMER_SERVICE_URL}/health", timeout=5)
        services['CustomerMS'] = {
            'status': 'online' if response.status_code == 200 else 'offline',
            'response_time': response.elapsed.total_seconds(),
            'details': response.json() if response.status_code == 200 else None
        }
    except:
        services['CustomerMS'] = {'status': 'offline', 'response_time': None, 'details': None}
    
    try:
        # Check InventoryMS
        response = requests.get(f"{Config.INVENTORY_SERVICE_URL}/health", timeout=5)
        services['InventoryMS'] = {
            'status': 'online' if response.status_code == 200 else 'offline',
            'response_time': response.elapsed.total_seconds(),
            'details': response.json() if response.status_code == 200 else None
        }
    except:
        services['InventoryMS'] = {'status': 'offline', 'response_time': None, 'details': None}
    
    try:
        # Check DeliveryMS
        response = requests.get(f"{Config.DELIVERY_SERVICE_URL}/health", timeout=5)
        services['DeliveryMS'] = {
            'status': 'online' if response.status_code == 200 else 'offline',
            'response_time': response.elapsed.total_seconds(),
            'details': response.json() if response.status_code == 200 else None
        }
    except:
        services['DeliveryMS'] = {'status': 'offline', 'response_time': None, 'details': None}
    
    return _success(services, "All services health checked via OrderMS gateway")

# === Error handler ===
@app.errorhandler(Exception)
def handle_any_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    logger.error(f"Error: {str(e)}")
    return jsonify({"error": str(e)}), code

if __name__ == "__main__":
    port = int(os.getenv("SERVICE_PORT", 5005))
    app.run(host="0.0.0.0", port=port, debug=True)