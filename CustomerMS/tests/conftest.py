import pytest
from app import app, db
import importlib
app_module = importlib.import_module('app')
import os
import sys

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    # Configure test database
    app.config['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
    app.config['DB_NAME'] = os.getenv('DB_NAME', 'levels_living_db_new')
    app.config['DB_USER'] = os.getenv('DB_USER', 'levels_user')
    app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD', 'levels_password')
    
    # Yield the Flask test client within an application context
    with app.test_client() as test_client:
        with app.app_context():
            yield test_client

@pytest.fixture
def mock_db(mocker):
    # Mock database connection and cursor
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    # default behavior: fetchone returns None, fetchall returns []
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_connection.cursor.return_value = mock_cursor
    
    # Mock db.get_connection to return our mock connection
    mocker.patch.object(db, 'get_connection', return_value=mock_connection)
    
    return {
        'connection': mock_connection,
        'cursor': mock_cursor
    }

@pytest.fixture
def auth_token(mocker):
    # Mock JWT verification and claims
    mock_jwt = {
        'sub': 'admin@levels.sg',
        'roles': ['admin', 'customer_service'],
        'role': 'admin'
    }

    def mock_verify_jwt(*args, **kwargs):
        # set claims directly on the request-local `g` (called during a request)
        from flask import g
        g._jwt_extended_jwt = mock_jwt
        return True

    # Create a mock function that returns our mock_jwt
    def mock_get_jwt():
        return mock_jwt

    def mock_get_jwt_identity():
        return 'admin@levels.sg'

    # Mock the required JWT functions
    # Patch the JWT functions that were imported into the app module
    # so the real @jwt_required() decorator inside app.py can run and
    # verify_jwt_in_request will set the expected claims into flask.g
    # Patch the functions on the app module (not the Flask instance)
    mocker.patch.object(app_module, 'verify_jwt_in_request', side_effect=mock_verify_jwt)
    mocker.patch.object(app_module, 'get_jwt', side_effect=mock_get_jwt)
    mocker.patch.object(app_module, 'get_jwt_identity', side_effect=mock_get_jwt_identity)

    # Also patch the underlying flask_jwt_extended implementations so
    # the real @jwt_required() decorator (which references these)
    # will call our mock and set flask.g correctly during tests.
    mocker.patch('flask_jwt_extended.view_decorators.verify_jwt_in_request', side_effect=mock_verify_jwt)
    mocker.patch('flask_jwt_extended.utils.get_jwt', side_effect=mock_get_jwt)
    mocker.patch('flask_jwt_extended.utils.get_jwt_identity', side_effect=mock_get_jwt_identity)

    return "test-token"