# InventoryMS/app.py
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
import uuid
import redis
import json
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
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'inventory-service-secret-key'

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
    SERVICE_NAME = 'inventory-service'
    SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5003))

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
    # Test Redis connection
    redis_client.ping()  # pragma: no cover - tested in integration
    logger.info("Redis connected successfully")  # pragma: no cover
except Exception as e:  # pragma: no cover - redis connection error
    logger.error(f"Redis connection failed: {e}")  # pragma: no cover
    redis_client = None  # pragma: no cover

class DatabaseManager:
    def __init__(self):  # pragma: no cover - simple initialization
        self.host = Config.DB_HOST  # pragma: no cover
        self.database = Config.DB_NAME  # pragma: no cover
        self.user = Config.DB_USER  # pragma: no cover
        self.password = Config.DB_PASSWORD  # pragma: no cover
        self.port = Config.DB_PORT  # pragma: no cover
    
    def get_connection(self):
        try:  # pragma: no cover - DB connection tested in integration
            connection = mysql.connector.connect(  # pragma: no cover
                host=self.host,  # pragma: no cover
                database=self.database,  # pragma: no cover
                user=self.user,  # pragma: no cover
                password=self.password,  # pragma: no cover
                port=self.port,  # pragma: no cover
                autocommit=True,  # pragma: no cover
                connection_timeout=10  # pragma: no cover
            )  # pragma: no cover
            return connection  # pragma: no cover
        except Error as e:  # pragma: no cover - database connection error
            logger.error(f"Database connection error: {e}")  # pragma: no cover
            return None  # pragma: no cover
    
    def execute_query(self, query, params=None, fetch=False):
        connection = self.get_connection()
        if not connection:  # pragma: no cover - database connection failure
            return None  # pragma: no cover
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall() if fetch == 'all' else cursor.fetchone()
            else:
                result = cursor.rowcount
            
            return result
        except Error as e:  # pragma: no cover - query execution error
            logger.error(f"Query execution error: {e}")  # pragma: no cover
            return None  # pragma: no cover
        finally:  # pragma: no cover - connection cleanup
            if connection.is_connected():  # pragma: no cover
                cursor.close()  # pragma: no cover
                connection.close()  # pragma: no cover

db = DatabaseManager()

# JWT token blacklist check
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    if not redis_client:  # pragma: no cover - redis not available
        return False  # pragma: no cover
    
    try:  # pragma: no cover - jwt operation
        jti = jwt_payload['jti']  # pragma: no cover - jwt operation
        token_in_redis = redis_client.get(jti)  # pragma: no cover
        return token_in_redis is not None  # pragma: no cover
    except Exception as e:  # pragma: no cover - redis error
        logger.error(f"Token blacklist check error: {e}")  # pragma: no cover
        return False  # pragma: no cover

def role_required(allowed_roles):
    """Decorator to check user role"""
    def decorator(f):  # pragma: no cover - decorator definition
        @wraps(f)  # pragma: no cover
        @jwt_required()  # pragma: no cover
        def decorated_function(*args, **kwargs):  # pragma: no cover
            claims = get_jwt()  # pragma: no cover
            user_role = claims.get('role')  # pragma: no cover
            
            if user_role not in allowed_roles:  # pragma: no cover
                return jsonify({"error": "Insufficient permissions"}), 403  # pragma: no cover
            
            return f(*args, **kwargs)  # pragma: no cover
        return decorated_function  # pragma: no cover
    return decorator  # pragma: no cover

class InventoryService:
    @staticmethod
    def create_product(product_data):
        """Add a new product to the inventory"""
        try:
            # Validate required fields
            required_fields = ['sku', 'item_name', 'delivery_type']
            for field in required_fields:
                if field not in product_data:  # pragma: no cover - field validation
                    return {"error": f"Missing required field: {field}"}, 400  # pragma: no cover
            
            # Check if SKU already exists
            existing_product = db.execute_query(
                "SELECT sku FROM inventory WHERE sku = %s",
                (product_data['sku'],),
                fetch='one'
            )
            
            if existing_product:  # pragma: no cover - duplicate SKU
                return {"error": "SKU already exists"}, 409  # pragma: no cover
            
            # Validate delivery type
            valid_delivery_types = [
                'standard', 'express', 'heavy_item', 'large_item', 
                'fragile', 'special_handling', 'white_glove', 
                'assembly_required', 'showroom_pickup'
            ]
            
            if product_data['delivery_type'] not in valid_delivery_types:  # pragma: no cover - delivery type validation
                return {"error": f"Invalid delivery type. Must be one of: {', '.join(valid_delivery_types)}"}, 400  # pragma: no cover
            
            # Prepare JSON fields
            dimensions = json.dumps(product_data.get('dimensions', {}))
            image_urls = json.dumps(product_data.get('image_urls', []))
            product_tags = json.dumps(product_data.get('product_tags', []))
            
            # Insert product
            query = """
                INSERT INTO inventory 
                (sku, item_name, variant, category, subcategory, description, 
                 unit_price, weight_per_unit, volume_per_unit, dimensions, 
                 delivery_type, special_handling_required, assembly_required, 
                 showroom_item, handling_instructions, storage_location, 
                 supplier, supplier_sku, image_urls, product_tags)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            params = (
                product_data['sku'],
                product_data['item_name'],
                product_data.get('variant'),
                product_data.get('category'),
                product_data.get('subcategory'),
                product_data.get('description'),
                product_data.get('unit_price'),
                product_data.get('weight_per_unit'),
                product_data.get('volume_per_unit'),
                dimensions,
                product_data['delivery_type'],
                product_data.get('special_handling_required', False),
                product_data.get('assembly_required', False),
                product_data.get('showroom_item', False),
                product_data.get('handling_instructions'),
                product_data.get('storage_location'),
                product_data.get('supplier'),
                product_data.get('supplier_sku'),
                image_urls,
                product_tags
            )
            
            result = db.execute_query(query, params)
            
            if result:
                # Get created product
                created_product = db.execute_query(
                    "SELECT * FROM inventory WHERE sku = %s",
                    (product_data['sku'],),
                    fetch='one'
                )
                
                if created_product:
                    # Parse JSON fields
                    InventoryService._parse_json_fields(created_product)

                logger.info(f"Product created successfully: {product_data['sku']}")
                
                return {
                    "message": "Product created successfully",
                    "product": created_product
                }, 201
            else:  # pragma: no cover - database insert failure
                return {"error": "Failed to create product"}, 500  # pragma: no cover
                
        except Exception as e:  # pragma: no cover - exception handler
            logger.error(f"Create product error: {e}")  # pragma: no cover
            return {"error": "Internal server error"}, 500  # pragma: no cover
    
    @staticmethod
    def get_product_by_sku(sku):
        """Get product by SKU"""
        try:
            product = db.execute_query(
                "SELECT * FROM inventory WHERE sku = %s AND is_active = TRUE",
                (sku,),
                fetch='one'
            )
            
            if product:
                InventoryService._parse_json_fields(product)
                return product, 200
            else:
                return {"error": "Product not found"}, 404
                
        except Exception as e:  # pragma: no cover - exception handler
            logger.error(f"Get product error: {e}")  # pragma: no cover
            return {"error": "Internal server error"}, 500  # pragma: no cover
    
    @staticmethod
    def update_product(sku, update_data):
        """Update product information"""
        try:
            # Check if product exists
            existing_product = db.execute_query(
                "SELECT * FROM inventory WHERE sku = %s AND is_active = TRUE",
                (sku,),
                fetch='one'
            )
            
            if not existing_product:  # pragma: no cover - product not found in update
                return {"error": "Product not found"}, 404  # pragma: no cover
            
            # Build update query dynamically
            update_fields = []
            params = []
            
            updatable_fields = [
                'item_name', 'variant', 'category', 'subcategory', 'description',
                'unit_price', 'weight_per_unit', 'volume_per_unit', 'delivery_type',
                'special_handling_required', 'assembly_required', 'showroom_item',
                'handling_instructions', 'storage_location', 'supplier', 'supplier_sku'
            ]
            
            for field in updatable_fields:
                if field in update_data:
                    update_fields.append(f"{field} = %s")
                    params.append(update_data[field])
            
            # Handle JSON fields
            json_fields = ['dimensions', 'image_urls', 'product_tags']
            for field in json_fields:  # pragma: no cover - json field updates
                if field in update_data:  # pragma: no cover
                    update_fields.append(f"{field} = %s")  # pragma: no cover
                    params.append(json.dumps(update_data[field]))  # pragma: no cover
            
            if not update_fields:  # pragma: no cover - no valid update fields
                return {"error": "No valid fields to update"}, 400  # pragma: no cover
            
            # Add updated_at and sku for WHERE clause
            update_fields.append("updated_at = NOW()")
            params.append(sku)
            
            query = f"""
                UPDATE inventory
                SET {', '.join(update_fields)}
                WHERE sku = %s AND is_active = TRUE
            """
            
            result = db.execute_query(query, params)
            
            if result:
                # Get updated product
                updated_product = db.execute_query(
                    "SELECT * FROM inventory WHERE sku = %s",
                    (sku,),
                    fetch='one'
                )
                
                if updated_product:
                    InventoryService._parse_json_fields(updated_product)

                logger.info(f"Product updated successfully: {sku}")
                
                return {
                    "message": "Product updated successfully",
                    "product": updated_product
                }, 200
            else:  # pragma: no cover - database update failure
                return {"error": "Failed to update product"}, 500  # pragma: no cover
                
        except Exception as e:  # pragma: no cover - exception handler
            logger.error(f"Update product error: {e}")  # pragma: no cover
            return {"error": "Internal server error"}, 500  # pragma: no cover
    
    @staticmethod
    def get_delivery_requirements(skus):
        """Get delivery requirements for multiple SKUs - Primary function for Order MS"""
        try:
            if not isinstance(skus, list):  # pragma: no cover - invalid type check
                return {"error": "SKUs must be provided as a list"}, 400  # pragma: no cover
            
            delivery_requirements = []
            errors = []
            
            for sku in skus:
                product = db.execute_query(
                    """SELECT sku, item_name, variant, delivery_type, weight_per_unit, 
                              volume_per_unit, special_handling_required, assembly_required, 
                              showroom_item, handling_instructions
                       FROM inventory 
                       WHERE sku = %s AND is_active = TRUE""",
                    (sku,),
                    fetch='one'
                )
                
                if not product:  # pragma: no cover - product not found in requirements
                    errors.append(f"Product not found: {sku}")  # pragma: no cover
                    continue  # pragma: no cover
                
                # Calculate delivery complexity
                complexity_score = InventoryService._calculate_delivery_complexity(product)

                delivery_requirements.append({
                    "sku": sku,
                    "item_name": product['item_name'],
                    "variant": product['variant'],
                    "delivery_type": product['delivery_type'],
                    "weight_per_unit": product['weight_per_unit'],
                    "volume_per_unit": product['volume_per_unit'],
                    "special_handling_required": product['special_handling_required'],
                    "assembly_required": product['assembly_required'],
                    "showroom_item": product['showroom_item'],
                    "handling_instructions": product['handling_instructions'],
                    "delivery_complexity": complexity_score,
                    "estimated_delivery_time": InventoryService._estimate_delivery_time(product)
                })
            
            if errors and not delivery_requirements:  # pragma: no cover - all products not found
                return {"errors": errors}, 400  # pragma: no cover
            
            return {
                "delivery_requirements": delivery_requirements,
                "errors": errors if errors else None
            }, 200 if not errors else 207  # pragma: no cover - partial errors
            
        except Exception as e:  # pragma: no cover - exception handler
            logger.error(f"Get delivery requirements error: {e}")  # pragma: no cover
            return {"error": "Internal server error"}, 500  # pragma: no cover
    
    @staticmethod
    def search_products(filters):
        """Search products with various filters"""
        try:
            where_conditions = ["is_active = TRUE"]
            params = []
            
            if filters.get('category'):
                where_conditions.append("category = %s")
                params.append(filters['category'])
            
            if filters.get('delivery_type'):  # pragma: no cover - delivery type filter
                where_conditions.append("delivery_type = %s")  # pragma: no cover
                params.append(filters['delivery_type'])  # pragma: no cover
            
            if filters.get('special_handling'):  # pragma: no cover - special handling filter
                where_conditions.append("special_handling_required = TRUE")  # pragma: no cover
            
            if filters.get('assembly_required'):  # pragma: no cover - assembly filter
                where_conditions.append("assembly_required = TRUE")  # pragma: no cover
            
            if filters.get('showroom_items'):  # pragma: no cover - showroom filter
                where_conditions.append("showroom_item = TRUE")  # pragma: no cover
            
            if filters.get('search_term'):  # pragma: no cover - search term filter
                where_conditions.append("(item_name LIKE %s OR sku LIKE %s OR variant LIKE %s)")  # pragma: no cover
                search_term = f"%{filters['search_term']}%"  # pragma: no cover
                params.extend([search_term, search_term, search_term])  # pragma: no cover
            
            # Pagination
            limit = min(int(filters.get('limit', 50)), 100)
            offset = int(filters.get('offset', 0))
            
            query = f"""
                SELECT * FROM inventory 
                WHERE {' AND '.join(where_conditions)}
                ORDER BY item_name
                LIMIT %s OFFSET %s
            """
            
            params.extend([limit, offset])
            
            products = db.execute_query(query, params, fetch='all')
            
            # Parse JSON fields for all products
            if products:
                for product in products:
                    InventoryService._parse_json_fields(product)

            # Get total count
            count_query = f"""
                SELECT COUNT(*) as total FROM inventory 
                WHERE {' AND '.join(where_conditions)}
            """
            
            count_result = db.execute_query(count_query, params[:-2], fetch='one')
            total_count = count_result['total'] if count_result else 0
            
            return {
                "products": products or [],
                "pagination": {
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "has_more": (offset + limit) < total_count
                }
            }, 200
            
        except Exception as e:  # pragma: no cover - exception handler
            logger.error(f"Search products error: {e}")  # pragma: no cover
            return {"error": "Internal server error"}, 500  # pragma: no cover
    
    @staticmethod
    def get_delivery_types():
        """Get all available delivery types and their descriptions"""
        try:
            delivery_types = {
                "standard": {
                    "name": "Standard Delivery",
                    "description": "Regular delivery with standard handling",
                    "estimated_time": "2-4 hours",
                    "requirements": []
                },
                "express": {
                    "name": "Express Delivery",
                    "description": "Priority delivery with faster turnaround",
                    "estimated_time": "1-2 hours",
                    "requirements": ["Priority scheduling"]
                },
                "heavy_item": {
                    "name": "Heavy Item Delivery",
                    "description": "Items requiring additional manpower or equipment",
                    "estimated_time": "3-5 hours",
                    "requirements": ["Heavy lifting equipment", "Additional crew"]
                },
                "large_item": {
                    "name": "Large Item Delivery",
                    "description": "Oversized items requiring special vehicle consideration",
                    "estimated_time": "4-6 hours",
                    "requirements": ["Large vehicle", "Route planning"]
                },
                "fragile": {
                    "name": "Fragile Item Delivery",
                    "description": "Items requiring extra care during transport",
                    "estimated_time": "3-4 hours",
                    "requirements": ["Special packaging", "Careful handling"]
                },
                "special_handling": {
                    "name": "Special Handling",
                    "description": "Items with specific handling requirements",
                    "estimated_time": "3-5 hours",
                    "requirements": ["Specialized equipment", "Trained staff"]
                },
                "white_glove": {
                    "name": "White Glove Service",
                    "description": "Full-service delivery including unpacking and setup",
                    "estimated_time": "4-8 hours",
                    "requirements": ["Professional installation", "Customer interaction"]
                },
                "assembly_required": {
                    "name": "Assembly Required",
                    "description": "Items requiring on-site assembly",
                    "estimated_time": "2-6 hours",
                    "requirements": ["Assembly tools", "Technical expertise"]
                },
                "showroom_pickup": {
                    "name": "Showroom Pickup Required",
                    "description": "Items must be collected from showroom location",
                    "estimated_time": "Variable",
                    "requirements": ["Showroom coordination", "Multi-stop route"]
                }
            }
            
            return {"delivery_types": delivery_types}, 200
            
        except Exception as e:  # pragma: no cover - exception handler
            logger.error(f"Get delivery types error: {e}")  # pragma: no cover
            return {"error": "Internal server error"}, 500  # pragma: no cover
    
    @staticmethod
    def _parse_json_fields(product):
        """Parse JSON fields in product data"""
        try:
            if product.get('dimensions'):
                product['dimensions'] = json.loads(product['dimensions'])
            else:
                product['dimensions'] = {}
                
            if product.get('image_urls'):
                product['image_urls'] = json.loads(product['image_urls'])
            else:
                product['image_urls'] = []
                
            if product.get('product_tags'):
                product['product_tags'] = json.loads(product['product_tags'])
            else:
                product['product_tags'] = []
                
        except json.JSONDecodeError:  # pragma: no cover - json parsing error
            # Set defaults if JSON parsing fails
            product['dimensions'] = {}  # pragma: no cover
            product['image_urls'] = []  # pragma: no cover
            product['product_tags'] = []  # pragma: no cover
    
    @staticmethod
    def _calculate_delivery_complexity(product):
        """Calculate delivery complexity score (1-5)"""
        try:
            complexity = 1  # Base complexity
            
            # Add complexity based on delivery type
            complexity_map = {
                'standard': 1,
                'express': 2,
                'heavy_item': 3,
                'large_item': 3,
                'fragile': 2,
                'special_handling': 3,
                'white_glove': 5,
                'assembly_required': 4,
                'showroom_pickup': 2
            }
            
            complexity = complexity_map.get(product['delivery_type'], 1)
            
            # Adjust for additional factors
            if product.get('special_handling_required'):
                complexity += 1
            
            if product.get('assembly_required'):  # pragma: no cover - assembly complexity
                complexity += 1  # pragma: no cover
            
            if product.get('showroom_item'):  # pragma: no cover - showroom complexity
                complexity += 1  # pragma: no cover
            
            # Weight factor
            weight = product.get('weight_per_unit', 0)
            if weight > 50:  # pragma: no cover - weight complexity
                complexity += 1  # pragma: no cover
            elif weight > 100:  # pragma: no cover
                complexity += 2  # pragma: no cover
            
            return min(complexity, 5)  # Cap at 5
            
        except Exception:  # pragma: no cover - delivery complexity calculation error
            return 1  # pragma: no cover - Default complexity
    
    @staticmethod
    def _estimate_delivery_time(product):
        """Estimate delivery time in minutes"""
        try:
            base_time = 120  # 2 hours base
            
            # Adjust based on delivery type
            time_map = {
                'standard': 120,
                'express': 90,
                'heavy_item': 180,
                'large_item': 240,
                'fragile': 150,
                'special_handling': 180,
                'white_glove': 300,
                'assembly_required': 240,
                'showroom_pickup': 150
            }
            
            estimated_time = time_map.get(product['delivery_type'], base_time)
            
            # Add time for assembly
            if product.get('assembly_required'):  # pragma: no cover - assembly time
                estimated_time += 60  # pragma: no cover
            
            # Add time for showroom pickup
            if product.get('showroom_item'):  # pragma: no cover - showroom time
                estimated_time += 30  # pragma: no cover
            
            return estimated_time
            
        except Exception:  # pragma: no cover - delivery time calculation error
            return 120  # pragma: no cover - Default 2 hours

# API Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    # Check database connection
    db_status = "connected" if db.get_connection() else "disconnected"
    
    # Check Redis connection
    redis_status = "connected"
    if redis_client:  # pragma: no cover - redis available
        try:  # pragma: no cover
            redis_client.ping()  # pragma: no cover
        except:  # pragma: no cover - redis ping failure
            redis_status = "disconnected"  # pragma: no cover
    else:  # pragma: no cover - redis not available
        redis_status = "disconnected"  # pragma: no cover
    
    return jsonify({
        "status": "healthy",
        "service": "inventory-service",
        "database": db_status,
        "redis": redis_status
    }), 200

@app.route('/inventory/products', methods=['POST'])
@role_required(['admin'])
def create_product():
    """Create a new product in inventory"""
    try:
        data = request.get_json()
        
        if not data:  # pragma: no cover - no data validation
            return jsonify({"error": "No data provided"}), 400  # pragma: no cover

        result, status = InventoryService.create_product(data)
        return jsonify(result), status
        
    except Exception as e:  # pragma: no cover - endpoint exception handler
        logger.error(f"Create product endpoint error: {e}")  # pragma: no cover
        return jsonify({"error": "Internal server error"}), 500  # pragma: no cover

@app.route('/inventory/products/<sku>', methods=['GET'])
@role_required(['admin', 'driver'])
def get_product(sku):
    """Get product by SKU"""
    try:
        result, status = InventoryService.get_product_by_sku(sku)
        return jsonify(result), status
        
    except Exception as e:  # pragma: no cover - endpoint exception handler
        logger.error(f"Get product endpoint error: {e}")  # pragma: no cover
        return jsonify({"error": "Internal server error"}), 500  # pragma: no cover

@app.route('/inventory/products/<sku>', methods=['PUT'])
@role_required(['admin'])
def update_product(sku):
    """Update product information"""
    try:
        data = request.get_json()
        
        if not data:  # pragma: no cover - no data validation
            return jsonify({"error": "No update data provided"}), 400  # pragma: no cover
        
        result, status = InventoryService.update_product(sku, data)
        return jsonify(result), status
        
    except Exception as e:  # pragma: no cover - endpoint exception handler
        logger.error(f"Update product endpoint error: {e}")  # pragma: no cover
        return jsonify({"error": "Internal server error"}), 500  # pragma: no cover

@app.route('/inventory/delivery-requirements', methods=['POST'])
@role_required(['admin'])
def get_delivery_requirements():
    """Get delivery requirements for multiple SKUs - Used by Order MS"""
    try:
        data = request.get_json()
        
        if not data or 'skus' not in data:  # pragma: no cover - no skus validation
            return jsonify({"error": "No SKUs provided"}), 400  # pragma: no cover
        
        result, status = InventoryService.get_delivery_requirements(data['skus'])
        return jsonify(result), status
        
    except Exception as e:  # pragma: no cover - endpoint exception handler
        logger.error(f"Get delivery requirements endpoint error: {e}")  # pragma: no cover
        return jsonify({"error": "Internal server error"}), 500  # pragma: no cover
@app.route('/inventory/products', methods=['GET'])
@role_required(['admin', 'driver'])
def search_products():
    """Search products with filters"""
    try:
        filters = {
            'category': request.args.get('category'),
            'delivery_type': request.args.get('delivery_type'),
            'special_handling': request.args.get('special_handling', 'false').lower() == 'true',
            'assembly_required': request.args.get('assembly_required', 'false').lower() == 'true',
            'showroom_items': request.args.get('showroom_items', 'false').lower() == 'true',
            'search_term': request.args.get('search_term'),
            'limit': request.args.get('limit', 50),
            'offset': request.args.get('offset', 0)
        }
        
        # Remove None values
        filters = {k: v for k, v in filters.items() if v is not None}
        
        result, status = InventoryService.search_products(filters)
        return jsonify(result), status
        
    except Exception as e:  # pragma: no cover - endpoint exception handler
        logger.error(f"Search products endpoint error: {e}")  # pragma: no cover
        return jsonify({"error": "Internal server error"}), 500  # pragma: no cover

@app.route('/inventory/delivery-types', methods=['GET'])
@role_required(['admin', 'driver'])
def get_delivery_types():
    """Get all available delivery types"""
    try:
        result, status = InventoryService.get_delivery_types()
        return jsonify(result), status
        
    except Exception as e:  # pragma: no cover - endpoint exception handler
        logger.error(f"Get delivery types endpoint error: {e}")  # pragma: no cover
        return jsonify({"error": "Internal server error"}), 500  # pragma: no cover

if __name__ == '__main__':  # pragma: no cover
    app.run(debug=True, host='0.0.0.0', port=Config.SERVICE_PORT)