# InventoryMS/tests/conftest.py
import pytest
import sys
import os

# Add parent directory to path to import app module
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app import app, db


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def mock_db(mocker):
    """Mock database connection and cursor"""
    mock_connection = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    
    # Configure cursor to return dictionaries like the real MySQL cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_cursor.rowcount = 0
    
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.commit.return_value = None
    mock_connection.close.return_value = None
    
    # Mock the db.get_connection method
    mocker.patch.object(db, 'get_connection', return_value=mock_connection)
    
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
