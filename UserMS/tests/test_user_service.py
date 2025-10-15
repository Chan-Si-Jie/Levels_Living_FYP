import pytest
from app import app
import json

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'service' in data
    assert 'database' in data
    assert 'redis' in data

def test_register_user(client, mock_db):
    """Test user registration endpoint"""
    mock_db['cursor'].fetchone.return_value = None  # No existing user
    mock_db['cursor'].rowcount = 1
    response = client.post('/auth/register', json={
        'email': 'testuser@levels.sg',
        'password': 'securePassword123!',
        'role': 'admin'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'user_id' in data
    assert data['role'] == 'admin'

def test_register_existing_user(client, mock_db):
    """Test registration with existing user"""
    mock_db['cursor'].fetchone.return_value = {'user_id': 'uuid-1234'}
    response = client.post('/auth/register', json={
        'email': 'testuser@levels.sg',
        'password': 'securePassword123!',
        'role': 'admin'
    })
    assert response.status_code == 409
    data = json.loads(response.data)
    assert data.get('error') == 'User already exists'

def test_login_success(client, mock_db):
    """Test successful login"""
    mock_db['cursor'].fetchone.return_value = {
        'user_id': 'uuid-1234',
        'email': 'testuser@levels.sg',
        'password_hash': 'hashed_pw',
        'role': 'admin',
        'is_active': True,
        'login_attempts': 0,
        'locked_until': None
    }
    response = client.post('/auth/login', json={
        'email': 'testuser@levels.sg',
        'password': 'securePassword123!'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert 'refresh_token' in data

def test_login_invalid_user(client, mock_db):
    """Test login with invalid credentials"""
    mock_db['cursor'].fetchone.return_value = None
    response = client.post('/auth/login', json={
        'email': 'wrong@levels.sg',
        'password': 'badpassword'
    })
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data.get('error') == 'Invalid credentials'

def test_get_user_profile(client, auth_token, mock_db):
    """Test retrieving user profile"""
    mock_db['cursor'].fetchone.return_value = {
        'user_id': 'uuid-1234',
        'email': 'testuser@levels.sg',
        'role': 'admin',
        'is_active': True,
        'last_login': '2025-10-15 10:00:00',
        'created_at': '2025-01-01 09:00:00'
    }
    response = client.get('/auth/profile', headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['email'] == 'testuser@levels.sg'
    assert data['role'] == 'admin'

def test_get_user_not_found(client, auth_token, mock_db):
    """Test retrieving non-existent user profile"""
    mock_db['cursor'].fetchone.return_value = None
    response = client.get('/auth/profile', headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data.get('error') == 'User not found'
