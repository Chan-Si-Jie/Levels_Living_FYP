import pytest
import sys
import os
from unittest.mock import MagicMock, patch, Mock

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Create mock Redis module before importing app
mock_redis_module = Mock()
mock_redis_class = MagicMock()
mock_redis_instance = MagicMock()
mock_redis_instance.ping.return_value = True
mock_redis_class.return_value = mock_redis_instance
mock_redis_module.Redis = mock_redis_class

# Patch both redis module and logging before importing app
sys.modules['redis'] = mock_redis_module

with patch('logging.getLogger') as mock_get_logger:
    # Set up mock logger
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
