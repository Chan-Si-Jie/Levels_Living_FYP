import pytest
from app import app
import json
import os


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'service' in data
    assert 'database' in data
    assert 'redis' in data


def test_health_check_redis_failure(client, mock_db, monkeypatch):
    """Test health check when Redis ping fails"""
    import app as app_module
    
    # Mock redis_client to raise exception on ping
    class MockRedis:
        def ping(self):
            raise Exception("Redis connection failed")
    
    original_redis = app_module.redis_client
    app_module.redis_client = MockRedis()
    
    try:
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['redis'] == 'disconnected'
    finally:
        app_module.redis_client = original_redis


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


def test_register_no_data(client, mocker):
    """Test registration with no data provided"""
    # Mock get_json to return None (simulating no JSON data)
    mocker.patch('flask.Request.get_json', return_value=None)
    
    response = client.post('/auth/register', content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'No data provided' in data['error']


def test_register_missing_email(client):
    """Test registration with missing email"""
    response = client.post('/auth/register', json={
        'password': 'securePassword123!',
        'role': 'admin'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Missing required field' in data['error']


def test_register_invalid_email(client):
    """Test registration with invalid email format"""
    response = client.post('/auth/register', json={
        'email': 'invalid-email',
        'password': 'securePassword123!',
        'role': 'admin'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Invalid email format' in data['error']


def test_register_invalid_role(client):
    """Test registration with invalid role"""
    response = client.post('/auth/register', json={
        'email': 'test@levels.sg',
        'password': 'securePassword123!',
        'role': 'invalid_role'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Invalid role' in data['error']


def test_register_weak_password(client):
    """Test registration with weak password"""
    response = client.post('/auth/register', json={
        'email': 'test@levels.sg',
        'password': 'weak',
        'role': 'admin'
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'at least 8 characters' in data['error']


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


def test_register_db_failure(client, mock_db):
    """Test registration when database insert fails"""
    mock_db['cursor'].fetchone.return_value = None
    mock_db['cursor'].rowcount = 0  # Insert failed
    
    response = client.post('/auth/register', json={
        'email': 'test@levels.sg',
        'password': 'securePassword123!',
        'role': 'admin'
    })
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'Failed to create user' in data['error']


def test_register_service_exception(client, mock_db):
    """Test registration when service layer raises exception"""
    # Make execute_query raise an exception
    mock_db['cursor'].execute.side_effect = Exception("Database connection lost")
    
    response = client.post('/auth/register', json={
        'email': 'test@levels.sg',
        'password': 'securePassword123!',
        'role': 'admin'
    })
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'Internal server error' in data['error']


def test_register_exception(client, mocker):
    """Test registration with exception in request handling"""
    # Mock get_json to raise an exception (not 415, but actual exception)
    mocker.patch('flask.Request.get_json', side_effect=Exception("Unexpected error"))
    
    response = client.post('/auth/register', json={'test': 'data'})
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'Internal server error' in data['error']


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


def test_login_no_data(client, mocker):
    """Test login with no data"""
    # Mock get_json to return None (simulating no JSON data)
    mocker.patch('flask.Request.get_json', return_value=None)
    
    response = client.post('/auth/login', content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'No data provided' in data['error']


def test_login_missing_credentials(client):
    """Test login with missing email or password"""
    response = client.post('/auth/login', json={'email': 'test@levels.sg'})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Email and password are required' in data['error']


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


def test_login_account_locked(client, mock_db):
    """Test login with locked account"""
    from datetime import datetime, timedelta
    
    mock_db['cursor'].fetchone.return_value = {
        'user_id': 'uuid-1234',
        'email': 'testuser@levels.sg',
        'password_hash': 'hashed_pw',
        'role': 'admin',
        'is_active': True,
        'login_attempts': 5,
        'locked_until': datetime.now() + timedelta(minutes=30)
    }
    
    response = client.post('/auth/login', json={
        'email': 'testuser@levels.sg',
        'password': 'securePassword123!'
    })
    assert response.status_code == 423
    data = json.loads(response.data)
    assert 'Account is temporarily locked' in data['error']


def test_login_inactive_account(client, mock_db):
    """Test login with inactive account"""
    mock_db['cursor'].fetchone.return_value = {
        'user_id': 'uuid-1234',
        'email': 'testuser@levels.sg',
        'password_hash': 'hashed_pw',
        'role': 'admin',
        'is_active': False,
        'login_attempts': 0,
        'locked_until': None
    }
    
    response = client.post('/auth/login', json={
        'email': 'testuser@levels.sg',
        'password': 'securePassword123!'
    })
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'Account is deactivated' in data['error']


def test_login_wrong_password(client, mock_db, mocker):
    """Test login with wrong password"""
    from werkzeug.security import generate_password_hash
    
    # Override the auto-patched password check for this test only
    mocker.patch('app.check_password_hash', return_value=False)
    
    mock_db['cursor'].fetchone.return_value = {
        'user_id': 'uuid-1234',
        'email': 'testuser@levels.sg',
        'password_hash': generate_password_hash('correct_password'),
        'role': 'admin',
        'is_active': True,
        'login_attempts': 0,
        'locked_until': None
    }
    
    response = client.post('/auth/login', json={
        'email': 'testuser@levels.sg',
        'password': 'wrong_password'
    })
    assert response.status_code == 401
    data = json.loads(response.data)
    assert 'Invalid credentials' in data['error']


def test_login_max_attempts_lockout(client, mock_db, mocker):
    """Test account lockout after max login attempts"""
    from werkzeug.security import generate_password_hash
    
    # Override the auto-patched password check for this test only
    mocker.patch('app.check_password_hash', return_value=False)
    
    mock_db['cursor'].fetchone.return_value = {
        'user_id': 'uuid-1234',
        'email': 'testuser@levels.sg',
        'password_hash': generate_password_hash('correct_password'),
        'role': 'admin',
        'is_active': True,
        'login_attempts': 4,  # One more attempt will lock
        'locked_until': None
    }
    
    response = client.post('/auth/login', json={
        'email': 'testuser@levels.sg',
        'password': 'wrong_password'
    })
    assert response.status_code == 401


def test_login_exception(client, mocker):
    """Test login with exception in request handling"""
    # Mock get_json to raise an exception
    mocker.patch('flask.Request.get_json', side_effect=Exception("Unexpected error"))
    
    response = client.post('/auth/login', json={'test': 'data'})
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'Internal server error' in data['error']


def test_login_service_exception(client, mock_db):
    """Test login when service layer raises exception"""
    # Make execute_query raise an exception
    mock_db['cursor'].execute.side_effect = Exception("Database connection lost")
    
    response = client.post('/auth/login', json={
        'email': 'test@levels.sg',
        'password': 'password123'
    })
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'Internal server error' in data['error']


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


def test_get_profile_exception(client, auth_token, mock_db):
    """Test get profile with exception"""
    mock_db['connection'].cursor.side_effect = Exception("Database error")
    
    response = client.get('/auth/profile', headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 500
    data = json.loads(response.data)
    assert 'Internal server error' in data['error']


def test_logout_success(client, auth_token):
    """Test successful logout"""
    response = client.post('/auth/logout', headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'Logout successful' in data['message']


def test_logout_redis_failure(client, auth_token, monkeypatch):
    """Test logout when Redis fails"""
    import app as app_module
    
    class MockRedis:
        def set(self, *args, **kwargs):
            raise Exception("Redis error")
    
    original_redis = app_module.redis_client
    app_module.redis_client = MockRedis()
    
    try:
        response = client.post('/auth/logout', headers={'Authorization': f'Bearer {auth_token}'})
        assert response.status_code == 200
    finally:
        app_module.redis_client = original_redis


def test_logout_exception(client, auth_token, monkeypatch):
    """Test logout with exception"""
    from flask_jwt_extended import get_jwt
    
    def mock_get_jwt():
        raise Exception("JWT error")
    
    monkeypatch.setattr('app.get_jwt', mock_get_jwt)
    
    response = client.post('/auth/logout', headers={'Authorization': f'Bearer {auth_token}'})
    # Should still handle gracefully
    assert response.status_code in [200, 500]


def test_validate_token_success(client, auth_token):
    """Test token validation"""
    response = client.post('/auth/validate', headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['valid'] == True
    assert 'user_id' in data
    assert 'role' in data


def test_validate_token_exception(client, auth_token, monkeypatch):
    """Test validate token with exception"""
    from flask_jwt_extended import get_jwt_identity
    
    def mock_get_identity():
        raise Exception("JWT error")
    
    monkeypatch.setattr('app.get_jwt_identity', mock_get_identity)
    
    response = client.post('/auth/validate', headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 500


def test_list_users_as_admin(client, auth_token, mock_db):
    """Test listing users as admin"""
    mock_db['cursor'].fetchall.return_value = [
        {
            'user_id': 'uuid-1',
            'email': 'user1@levels.sg',
            'role': 'admin',
            'is_active': True,
            'last_login': '2025-10-15',
            'created_at': '2025-01-01'
        },
        {
            'user_id': 'uuid-2',
            'email': 'user2@levels.sg',
            'role': 'driver',
            'is_active': True,
            'last_login': '2025-10-14',
            'created_at': '2025-01-02'
        }
    ]
    
    # First call for role check
    mock_db['cursor'].fetchone.return_value = {
        'user_id': 'uuid-1234',
        'email': 'admin@levels.sg',
        'role': 'admin',
        'is_active': True,
        'last_login': '2025-10-15',
        'created_at': '2025-01-01'
    }
    
    response = client.get('/auth/users', headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'users' in data
    assert len(data['users']) == 2


def test_list_users_as_non_admin(client, auth_token, mock_db):
    """Test listing users as non-admin (should fail)"""
    mock_db['cursor'].fetchone.return_value = {
        'user_id': 'uuid-1234',
        'email': 'driver@levels.sg',
        'role': 'driver',  # Not admin
        'is_active': True,
        'last_login': '2025-10-15',
        'created_at': '2025-01-01'
    }
    
    response = client.get('/auth/users', headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 403
    data = json.loads(response.data)
    assert 'Insufficient permissions' in data['error']


def test_list_users_exception(client, auth_token, mock_db):
    """Test list users with exception"""
    # Make the database query raise an exception
    mock_db['connection'].cursor.side_effect = Exception("Database error")
    
    response = client.get('/auth/users', headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code in [404, 500]  # Could fail at role check or list query


def test_role_decorator_user_not_found(client, auth_token, mock_db):
    """Test role decorator when user not found"""
    mock_db['cursor'].fetchone.return_value = None
    
    response = client.get('/auth/users', headers={'Authorization': f'Bearer {auth_token}'})
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'User not found' in data['error']


def test_jwt_blacklist_no_redis(client, auth_token, monkeypatch):
    """Test JWT blacklist check when Redis is None"""
    import app as app_module
    
    original_redis = app_module.redis_client
    app_module.redis_client = None
    
    try:
        # Should still work without Redis
        response = client.post('/auth/validate', headers={'Authorization': f'Bearer {auth_token}'})
        assert response.status_code == 200
    finally:
        app_module.redis_client = original_redis


def test_jwt_blacklist_redis_exception(client, auth_token, monkeypatch):
    """Test JWT blacklist check with Redis exception"""
    import app as app_module
    
    class MockRedis:
        def get(self, key):
            raise Exception("Redis error")
    
    original_redis = app_module.redis_client
    app_module.redis_client = MockRedis()
    
    try:
        # Should handle exception gracefully
        response = client.post('/auth/validate', headers={'Authorization': f'Bearer {auth_token}'})
        # Token should be considered valid if Redis check fails
        assert response.status_code == 200
    finally:
        app_module.redis_client = original_redis
