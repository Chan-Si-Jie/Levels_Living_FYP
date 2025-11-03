# NotificationMS/app.py
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
import uuid
import redis
from datetime import datetime, timedelta
import logging
from functools import wraps
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

# Configure logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('mysql.connector').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Configuration class
class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'notification-service-secret-key'

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
    SERVICE_NAME = 'notification-service'
    SERVICE_PORT = int(os.environ.get('SERVICE_PORT', 5006))

    # Twilio Configuration
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    TWILIO_WHATSAPP_NUMBER = os.environ.get('TWILIO_WHATSAPP_NUMBER')  # Format: whatsapp:+1234567890
    TWILIO_WHATSAPP_CONTENT_SID = os.environ.get('TWILIO_WHATSAPP_CONTENT_SID')  # WhatsApp template content SID

    # SendGrid Configuration (Twilio's email service)
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    SENDGRID_FROM_EMAIL = os.environ.get('SENDGRID_FROM_EMAIL')
    SENDGRID_FROM_NAME = os.environ.get('SENDGRID_FROM_NAME') or 'Levels Living'

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for all routes
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "null"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )
    redis_client.ping()
    logger.info("Redis connection established")
except Exception as e:
    logger.error(f"Redis connection failed: {e}")
    redis_client = None

# Initialize Twilio client
twilio_client = None
if app.config['TWILIO_ACCOUNT_SID'] and app.config['TWILIO_AUTH_TOKEN']:
    try:
        twilio_client = Client(
            app.config['TWILIO_ACCOUNT_SID'],
            app.config['TWILIO_AUTH_TOKEN']
        )
        logger.info("Twilio client initialized successfully")
    except Exception as e:
        logger.error(f"Twilio initialization failed: {e}")
else:
    logger.warning("Twilio credentials not configured")

# Initialize SendGrid client
sendgrid_client = None
if app.config['SENDGRID_API_KEY']:
    try:
        sendgrid_client = SendGridAPIClient(app.config['SENDGRID_API_KEY'])
        logger.info("SendGrid client initialized successfully")
    except Exception as e:
        logger.error(f"SendGrid initialization failed: {e}")
else:
    logger.warning("SendGrid API key not configured")

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

# JWT token blacklist check
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    if not redis_client:
        return False
    jti = jwt_payload['jti']
    return redis_client.get(f"blacklist:{jti}") is not None

# Auth decorator
def auth_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

# Role-based access control decorator
def role_required(allowed_roles):
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

class NotificationService:
    """Service class for handling notifications"""
    
    @staticmethod
    def send_sms(to_number, message, notification_type='general'):
        """Send SMS via Twilio"""
        if not twilio_client:
            logger.error("Twilio client not initialized")
            return None, "Twilio service not available", 503
        
        if not app.config['TWILIO_PHONE_NUMBER']:
            logger.error("Twilio phone number not configured")
            return None, "Twilio phone number not configured", 500
        
        try:
            # Ensure phone number is in E.164 format
            if not to_number.startswith('+'):
                to_number = '+' + to_number
            
            message_obj = twilio_client.messages.create(
                body=message,
                from_=app.config['TWILIO_PHONE_NUMBER'],
                to=to_number
            )
            
            # Log notification to database
            notification_id = NotificationService.log_notification(
                recipient=to_number,
                message=message,
                channel='sms',
                notification_type=notification_type,
                external_id=message_obj.sid,
                status='sent'
            )
            
            logger.info(f"SMS sent successfully. SID: {message_obj.sid}")
            return {
                'notification_id': notification_id,
                'message_sid': message_obj.sid,
                'status': message_obj.status,
                'to': to_number
            }, None, 200
            
        except TwilioRestException as e:
            logger.error(f"Twilio SMS error: {e}")
            
            # Log failed notification
            NotificationService.log_notification(
                recipient=to_number,
                message=message,
                channel='sms',
                notification_type=notification_type,
                status='failed',
                error_message=str(e)
            )
            
            return None, f"Failed to send SMS: {str(e)}", 500
    
    @staticmethod
    def send_whatsapp(to_number, time, notification_type='general'):
        """Send WhatsApp message via Twilio with template"""
        if not twilio_client:
            logger.error("Twilio client not initialized")
            return None, "Twilio service not available", 503
        
        if not app.config['TWILIO_WHATSAPP_NUMBER']:
            logger.error("Twilio WhatsApp number not configured")
            return None, "Twilio WhatsApp number not configured", 500
        
        try:
            # Format WhatsApp number for recipient
            if not to_number.startswith('whatsapp:'):
                if not to_number.startswith('+'):
                    to_number = '+' + to_number
                to_number = f'whatsapp:{to_number}'
            
            # Format WhatsApp number for sender (from)
            from_number = app.config['TWILIO_WHATSAPP_NUMBER']
            if not from_number.startswith('whatsapp:'):
                if not from_number.startswith('+'):
                    from_number = '+' + from_number
                from_number = f'whatsapp:{from_number}'
            
            # Prepare message content for logging
            message_content = f"Your delivery will be arriving in {time}. Thank you for ordering with Levels Living :)"
            
            # Check if content_sid is configured (for WhatsApp templates)
            if app.config.get('TWILIO_WHATSAPP_CONTENT_SID'):
                message_obj = twilio_client.messages.create(
                    from_=from_number,
                    to=to_number,
                    content_sid=app.config['TWILIO_WHATSAPP_CONTENT_SID'],
                    content_variables=f'{{"1":"{time}"}}'
                )
            else:
                # Send regular text message (for sandbox mode)
                message_obj = twilio_client.messages.create(
                    body=message_content,
                    from_=from_number,
                    to=to_number
                )
            
            # Log notification to database
            notification_id = NotificationService.log_notification(
                recipient=to_number,
                message=message_content,
                channel='whatsapp',
                notification_type=notification_type,
                external_id=message_obj.sid,
                status='sent'
            )
            
            logger.info(f"WhatsApp sent successfully. SID: {message_obj.sid}")
            return {
                'notification_id': notification_id,
                'message_sid': message_obj.sid,
                'status': message_obj.status,
                'to': to_number
            }, None, 200
            
        except TwilioRestException as e:
            logger.error(f"Twilio WhatsApp error: {e}")
            
            # Log failed notification
            NotificationService.log_notification(
                recipient=to_number,
                message=message_content if 'message_content' in locals() else f"Template delivery message (time: {time})",
                channel='whatsapp',
                notification_type=notification_type,
                status='failed',
                error_message=str(e)
            )
            
            return None, f"Failed to send WhatsApp: {str(e)}", 500
    
    @staticmethod
    def send_email(to_email, subject, message, notification_type='general', html_content=None):
        """Send email via SendGrid (Twilio's email service)"""
        if not sendgrid_client:
            logger.error("SendGrid client not initialized")
            return None, "SendGrid service not available", 503
        
        if not app.config['SENDGRID_FROM_EMAIL']:
            logger.error("SendGrid from email not configured")
            return None, "SendGrid from email not configured", 500
        
        try:
            # Create email message
            from_email = Email(
                app.config['SENDGRID_FROM_EMAIL'],
                app.config['SENDGRID_FROM_NAME']
            )
            to_email_obj = To(to_email)
            
            # Use HTML content if provided, otherwise plain text
            if html_content:
                content = Content("text/html", html_content)
            else:
                content = Content("text/plain", message)
            
            mail = Mail(from_email, to_email_obj, subject, content)
            
            # Send email
            response = sendgrid_client.send(mail)
            
            # Log notification to database
            notification_id = NotificationService.log_notification(
                recipient=to_email,
                message=f"Subject: {subject}\n\n{message}",
                channel='email',
                notification_type=notification_type,
                external_id=response.headers.get('X-Message-Id'),
                status='sent'
            )
            
            logger.info(f"Email sent successfully to {to_email}")
            return {
                'notification_id': notification_id,
                'status_code': response.status_code,
                'to': to_email,
                'subject': subject
            }, None, 200
            
        except Exception as e:
            logger.error(f"SendGrid email error: {e}")
            
            # Log failed notification
            NotificationService.log_notification(
                recipient=to_email,
                message=f"Subject: {subject}\n\n{message}",
                channel='email',
                notification_type=notification_type,
                status='failed',
                error_message=str(e)
            )
            
            return None, f"Failed to send email: {str(e)}", 500
    
    @staticmethod
    def log_notification(recipient, message, channel, notification_type, 
                        external_id=None, status='pending', error_message=None,
                        order_id=None, customer_id=None):
        """Log notification to database"""
        connection = get_db_connection()
        if not connection:
            logger.error("Cannot log notification: Database connection failed")
            return None
        
        try:
            cursor = connection.cursor()
            notification_id = str(uuid.uuid4())
            
            query = """
                INSERT INTO notifications 
                (notification_id, recipient, message, channel, notification_type,
                 external_id, status, error_message, order_id, customer_id, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                notification_id, recipient, message, channel, notification_type,
                external_id, status, error_message, order_id, customer_id,
                datetime.now()
            ))
            
            cursor.close()
            connection.close()
            
            logger.info(f"Notification logged: {notification_id}")
            return notification_id
            
        except Error as e:
            logger.error(f"Failed to log notification: {e}")
            return None
    
    @staticmethod
    def get_notification_history(limit=50, offset=0, channel=None, status=None):
        """Get notification history with pagination"""
        connection = get_db_connection()
        if not connection:
            return None, "Database connection failed", 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Build query with optional filters
            conditions = []
            params = []
            
            if channel:
                conditions.append("channel = %s")
                params.append(channel)
            
            if status:
                conditions.append("status = %s")
                params.append(status)
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            
            query = f"""
                SELECT * FROM notifications
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            notifications = cursor.fetchall()
            
            # Get total count
            count_query = f"SELECT COUNT(*) as total FROM notifications WHERE {where_clause}"
            cursor.execute(count_query, params[:-2] if conditions else [])
            total = cursor.fetchone()['total']
            
            cursor.close()
            connection.close()
            
            return {
                'notifications': notifications,
                'total': total,
                'limit': limit,
                'offset': offset
            }, None, 200
            
        except Error as e:
            logger.error(f"Failed to get notification history: {e}")
            return None, "Internal server error", 500

# API Routes
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    db_status = "connected" if get_db_connection() else "disconnected"
    redis_status = "connected"
    if redis_client:
        try:
            redis_client.ping()
        except:
            redis_status = "disconnected"
    else:
        redis_status = "disconnected"
    
    twilio_status = "configured" if twilio_client else "not configured"
    sendgrid_status = "configured" if sendgrid_client else "not configured"
    
    return jsonify({
        "service": app.config['SERVICE_NAME'],
        "status": "ok",
        "database": db_status,
        "redis": redis_status,
        "twilio": twilio_status,
        "sendgrid": sendgrid_status,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/notifications/sms', methods=['POST'])
@auth_required
def send_sms_notification():
    """Send SMS notification"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Request body required"}), 400
    
    to_number = data.get('to')
    message = data.get('message')
    notification_type = data.get('type', 'general')
    
    if not to_number or not message:
        return jsonify({"error": "to and message are required"}), 400
    
    result, error, status = NotificationService.send_sms(to_number, message, notification_type)
    
    if error:
        return jsonify({"error": error}), status
    
    return jsonify(result), status

@app.route('/notifications/sms/test', methods=['POST'])
def send_sms_test():
    """Send SMS notification (NO AUTH - FOR TESTING ONLY)"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Request body required"}), 400
    
    to_number = data.get('to')
    message = data.get('message')
    notification_type = data.get('type', 'test')
    
    if not to_number or not message:
        return jsonify({"error": "to and message are required"}), 400
    
    result, error, status = NotificationService.send_sms(to_number, message, notification_type)
    
    if error:
        return jsonify({"error": error}), status
    
    return jsonify(result), status

@app.route('/notifications/whatsapp', methods=['POST'])
@auth_required
def send_whatsapp_notification():
    """Send WhatsApp notification"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Request body required"}), 400
    
    to_number = data.get('to')
    time = data.get('time')
    notification_type = data.get('type', 'general')
    
    if not to_number or not time:
        return jsonify({"error": "to and time are required"}), 400
    
    result, error, status = NotificationService.send_whatsapp(to_number, time, notification_type)
    
    if error:
        return jsonify({"error": error}), status
    
    return jsonify(result), status

@app.route('/notifications/whatsapp/test', methods=['POST'])
def send_whatsapp_test():
    """Send WhatsApp notification (NO AUTH - FOR TESTING ONLY)"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Request body required"}), 400
    
    to_number = data.get('to')
    time = data.get('time')
    notification_type = data.get('type', 'test')
    
    if not to_number or not time:
        return jsonify({"error": "to and time are required"}), 400
    
    result, error, status = NotificationService.send_whatsapp(to_number, time, notification_type)
    
    if error:
        return jsonify({"error": error}), status
    
    return jsonify(result), status

@app.route('/notifications/email', methods=['POST'])
@auth_required
def send_email_notification():
    """Send email notification"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Request body required"}), 400
    
    to_email = data.get('to')
    subject = data.get('subject')
    message = data.get('message')
    html_content = data.get('html')
    notification_type = data.get('type', 'general')
    
    if not to_email or not subject or not message:
        return jsonify({"error": "to, subject, and message are required"}), 400
    
    result, error, status = NotificationService.send_email(
        to_email, subject, message, notification_type, html_content
    )
    
    if error:
        return jsonify({"error": error}), status
    
    return jsonify(result), status

@app.route('/notifications/email/test', methods=['POST'])
def send_email_test():
    """Send email notification (NO AUTH - FOR TESTING ONLY)"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Request body required"}), 400
    
    to_email = data.get('to')
    subject = data.get('subject')
    message = data.get('message')
    html_content = data.get('html')
    notification_type = data.get('type', 'test')
    
    if not to_email or not subject or not message:
        return jsonify({"error": "to, subject, and message are required"}), 400
    
    result, error, status = NotificationService.send_email(
        to_email, subject, message, notification_type, html_content
    )
    
    if error:
        return jsonify({"error": error}), status
    
    return jsonify(result), status

@app.route('/notifications/order/<order_id>/delivered', methods=['POST'])
@auth_required
def notify_order_delivered(order_id):
    """Send delivery confirmation notification"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Request body required"}), 400
    
    phone_number = data.get('phone_number')
    customer_name = data.get('customer_name', 'Customer')
    order_number = data.get('order_number', order_id)
    channel = data.get('channel', 'sms')  # sms or whatsapp
    
    if not phone_number:
        return jsonify({"error": "phone_number is required"}), 400
    
    if channel == 'whatsapp':
        # WhatsApp template expects just the time
        time = "just now"
        result, error, status = NotificationService.send_whatsapp(phone_number, time, 'delivery_confirmation')
    else:
        message = f"Hi {customer_name}, your order {order_number} has been delivered successfully. Thank you for choosing Levels Living!"
        result, error, status = NotificationService.send_sms(phone_number, message, 'delivery_confirmation')
    
    if error:
        return jsonify({"error": error}), status
    
    return jsonify(result), status

@app.route('/notifications/order/<order_id>/out-for-delivery', methods=['POST'])
@auth_required
def notify_out_for_delivery(order_id):
    """Send out-for-delivery notification"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Request body required"}), 400
    
    phone_number = data.get('phone_number')
    customer_name = data.get('customer_name', 'Customer')
    order_number = data.get('order_number', order_id)
    eta = data.get('eta', 'soon')
    channel = data.get('channel', 'sms')
    
    if not phone_number:
        return jsonify({"error": "phone_number is required"}), 400
    
    if channel == 'whatsapp':
        # WhatsApp template expects just the time/eta
        result, error, status = NotificationService.send_whatsapp(phone_number, eta, 'out_for_delivery')
    else:
        message = f"Hi {customer_name}, your order {order_number} is out for delivery. Expected arrival: {eta}. Levels Living"
        result, error, status = NotificationService.send_sms(phone_number, message, 'out_for_delivery')
    
    if error:
        return jsonify({"error": error}), status
    
    return jsonify(result), status

@app.route('/notifications/history', methods=['GET'])
@role_required(['admin'])
def get_notification_history():
    """Get notification history (admin only)"""
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    channel = request.args.get('channel')
    status = request.args.get('status')
    
    result, error, status_code = NotificationService.get_notification_history(
        limit=limit,
        offset=offset,
        channel=channel,
        status=status
    )
    
    if error:
        return jsonify({"error": error}), status_code
    
    return jsonify(result), status_code

@app.route('/notifications/<notification_id>', methods=['GET'])
@auth_required
def get_notification(notification_id):
    """Get specific notification details"""
    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM notifications WHERE notification_id = %s"
        cursor.execute(query, (notification_id,))
        notification = cursor.fetchone()
        
        cursor.close()
        connection.close()
        
        if not notification:
            return jsonify({"error": "Notification not found"}), 404
        
        return jsonify(notification), 200
        
    except Error as e:
        logger.error(f"Failed to get notification: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

def start_server():
    """Start the Flask development server."""
    port = int(os.getenv("SERVICE_PORT", 5006))
    debug = os.getenv("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)

if __name__ == "__main__":  # pragma: no cover
    start_server()
