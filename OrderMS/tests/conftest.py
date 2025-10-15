# OrderMS/tests/conftest.py
import pytest
import sys
import os

# Add parent directory to path to import app module
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
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
    
    # Also need to patch the orchestrator's db connection since it's initialized on import
    # We'll patch it by re-initializing the orchestrator with our mock
    from app import orchestrator
    orchestrator.db = mock_connection
    
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


@pytest.fixture
def mock_service_clients(mocker):
    """Mock external service client requests"""
    # Mock requests.request to avoid actual HTTP calls to other microservices
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = {}
    mock_response.raise_for_status.return_value = None
    
    mocker.patch('requests.request', return_value=mock_response)
    
    return mock_response
