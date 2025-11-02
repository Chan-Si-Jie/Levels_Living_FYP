import pytest
import sys
import os
from unittest.mock import MagicMock, patch, Mock

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Set test environment variables before importing app
os.environ['TESTING'] = 'True'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_NAME'] = 'test_db'
os.environ['DB_USER'] = 'test_user'
os.environ['DB_PASSWORD'] = 'test_pass'
os.environ['REDIS_HOST'] = 'localhost'
os.environ['TWILIO_ACCOUNT_SID'] = 'test_sid'
os.environ['TWILIO_AUTH_TOKEN'] = 'test_token'
os.environ['TWILIO_PHONE_NUMBER'] = '+1234567890'
os.environ['TWILIO_WHATSAPP_NUMBER'] = 'whatsapp:+14155238886'

# Create mock modules before importing app
mock_redis_module = Mock()
mock_redis_class = MagicMock()
mock_redis_instance = MagicMock()
mock_redis_instance.ping.return_value = True
mock_redis_class.return_value = mock_redis_instance
mock_redis_module.Redis = mock_redis_class
sys.modules['redis'] = mock_redis_module

# Mock mysql.connector before import
mock_mysql_connector_module = Mock()
mock_mysql_connector_module.Error = Exception
mock_mysql_connector_module.connect = MagicMock()

# Create parent mysql module
mock_mysql_module = Mock()
mock_mysql_module.connector = mock_mysql_connector_module

sys.modules['mysql'] = mock_mysql_module
sys.modules['mysql.connector'] = mock_mysql_connector_module

# Mock Twilio before import
mock_twilio_module = Mock()
mock_twilio_rest_module = Mock()
mock_twilio_client_class = MagicMock()
mock_twilio_rest_module.Client = mock_twilio_client_class
mock_twilio_module.rest = mock_twilio_rest_module
mock_twilio_module.base = Mock()
mock_twilio_module.base.exceptions = Mock()

class MockTwilioRestException(Exception):
    def __init__(self, status, uri, msg='', code=None, method='POST'):
        self.status = status
        self.uri = uri
        self.msg = msg
        self.code = code
        self.method = method
        super().__init__(f"HTTP {status} error: Unable to create record: {msg}")

mock_twilio_module.base.exceptions.TwilioRestException = MockTwilioRestException
sys.modules['twilio'] = mock_twilio_module
sys.modules['twilio.rest'] = mock_twilio_rest_module
sys.modules['twilio.base'] = mock_twilio_module.base
sys.modules['twilio.base.exceptions'] = mock_twilio_module.base.exceptions

# Mock logging
with patch('logging.getLogger') as mock_get_logger:
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger
    
    # Import app - this will use our mocks during initialization
    from app import app as flask_app
    
    # Store the mock logger for assertions in tests if needed
    flask_app._test_mock_logger = mock_logger


@pytest.fixture
def client():
    """Create test client for the Flask app"""
    flask_app.config['TESTING'] = True
    
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client


@pytest.fixture
def mock_db(mocker):
    """Mock database connection"""
    mock_connection = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    
    # Configure cursor to return dictionaries like the real MySQL cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_cursor.rowcount = 0
    mock_cursor.execute.return_value = None
    
    # Mock cursor() to return a new mock cursor with dictionary=True support
    def cursor_factory(dictionary=False):
        return mock_cursor
    
    mock_connection.cursor.side_effect = cursor_factory
    mock_connection.commit.return_value = None
    mock_connection.close.return_value = None
    
    # Mock the get_db_connection function
    mocker.patch('app.get_db_connection', return_value=mock_connection)
    
    return mock_cursor


@pytest.fixture
def auth_token(mocker):
    """Mock JWT authentication to simulate authenticated requests"""
    # Mock the verify_jwt_in_request function to do nothing (skip actual JWT verification)
    def mock_verify_jwt(*args, **kwargs):
        # Simulate setting JWT claims in flask.g
        from flask import g
        g._jwt_extended_jwt = {
            'sub': 'test-user-id',
            'role': 'admin'
        }
        g._jwt_extended_jwt_user = {
            'user_id': 'test-user-id',
            'role': 'admin'
        }
    
    mocker.patch('flask_jwt_extended.view_decorators.verify_jwt_in_request', side_effect=mock_verify_jwt)
    
    # Mock get_jwt_identity to return test user ID
    mocker.patch('flask_jwt_extended.utils.get_jwt_identity', return_value='test-user-id')
    
    # Mock get_jwt to return role information
    mocker.patch('flask_jwt_extended.utils.get_jwt', return_value={
        'sub': 'test-user-id',
        'role': 'admin'
    })
    
    # Return a dummy token string for tests that need it in headers
    return "test-token-123"


@pytest.fixture
def mock_redis(mocker):
    """Mock Redis client"""
    mock_redis = mocker.MagicMock()
    mocker.patch('app.redis_client', mock_redis)
    return mock_redis

@pytest.fixture
def mock_twilio_client(mocker):
    """Mock Twilio client"""
    return mocker.MagicMock()
