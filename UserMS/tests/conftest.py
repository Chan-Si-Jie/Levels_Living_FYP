import pytest
import os
import sys
# Ensure UserMS is in sys.path for import
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
from app import app, db
import os
import sys
import importlib

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
    app.config['DB_NAME'] = os.getenv('DB_NAME', 'levels_living_db_new')
    app.config['DB_USER'] = os.getenv('DB_USER', 'levels_user')
    app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD', 'levels_password')
    with app.test_client() as test_client:
        with app.app_context():
            yield test_client

@pytest.fixture
def mock_db(mocker):
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch.object(db, 'get_connection', return_value=mock_connection)
    return {
        'connection': mock_connection,
        'cursor': mock_cursor
    }

@pytest.fixture(autouse=True)
def mock_password_check(mocker):
    """Mock password hash check to always return True for tests"""
    # Patch where it's used in app.py
    mocker.patch('app.check_password_hash', return_value=True)

@pytest.fixture
def auth_token(mocker):
    mock_jwt = {
        'sub': 'admin@levels.sg',
        'roles': ['admin', 'user_service'],
        'role': 'admin'
    }
    def mock_verify_jwt(*args, **kwargs):
        from flask import g
        g._jwt_extended_jwt = mock_jwt
        return True
    def mock_get_jwt():
        return mock_jwt
    def mock_get_jwt_identity():
        return 'admin@levels.sg'
    # Only patch the flask_jwt_extended package-level functions
    mocker.patch('flask_jwt_extended.view_decorators.verify_jwt_in_request', side_effect=mock_verify_jwt)
    mocker.patch('flask_jwt_extended.utils.get_jwt', side_effect=mock_get_jwt)
    mocker.patch('flask_jwt_extended.utils.get_jwt_identity', side_effect=mock_get_jwt_identity)
    return "test-token"
