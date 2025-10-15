import pytest
from app import app
import json
from flask import g

def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert 'service' in data
    assert 'database' in data
    assert 'redis' in data

def test_create_customer_unauthorized(client):
    """Test creating a customer without authorization"""
    response = client.post('/customers', json={
        'customer_contact': '+6591234567',
        'customer_postal_code': '238123',
        'customer_street': 'Orchard Road',
        'customer_unit': '#01-01',
        'housing_type': 'HDB'
    })
    assert response.status_code == 401

def test_create_customer_authorized(client, auth_token, mock_db):
    """Test creating a customer with valid authorization"""
    # Mock the database response for geocoding check
    # Mock the DB sequence: first call (existence check) -> None, second call (select created) -> created dict
    created_customer = {
        'customer_id': 'uuid-1234',
        'customer_contact': '+6591234567',
        'customer_postal_code': '238123',
        'customer_street': 'Orchard Road',
        'customer_unit': '#01-01',
        'housing_type': 'HDB',
        'delivery_preferences': json.dumps({'time_slot': 'morning'}),
        'communication_preferences': json.dumps({'sms': True}),
        'latitude': 1.3521,
        'longitude': 103.8198
    }

    # Indicate no existing customer, then return the created customer on the following fetch
    mock_db['cursor'].fetchone.side_effect = [None, created_customer]
    # Simulate successful insert
    mock_db['cursor'].rowcount = 1

    response = client.post(
            '/customers',
            json={
                'customer_contact': '+6591234567',
                'customer_postal_code': '238123',
                'customer_street': 'Orchard Road',
                'customer_unit': '#01-01',
                'housing_type': 'HDB',
                'delivery_preferences': {
                    'time_slot': 'morning',
                    'special_instructions': 'Leave at door'
                },
                'communication_preferences': {
                    'sms': True,
                    'email': False
                }
            },
            headers={'Authorization': f'Bearer {auth_token}'}
        )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    # service returns {'message':..., 'customer': {...}}
    assert 'customer' in data
    assert data['message'] == 'Customer created successfully'

def test_get_customer_not_found(client, auth_token, mock_db):
    """Test getting a non-existent customer"""
    # Mock the database connection and cursor
    mock_db['cursor'].execute.return_value = True
    mock_db['cursor'].fetchone.return_value = None
    
    response = client.get(
            '/customers/999',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
    
    assert response.status_code == 404
    data = json.loads(response.data)
    # service returns {'error': 'Customer not found'} on 404
    assert data.get('error') in ('Customer not found', 'Customer not found')

def test_search_customers(client, auth_token, mock_db):
    """Test searching for customers"""
    # Mock the database response
    mock_db['cursor'].execute.return_value = True
    mock_db['cursor'].fetchall.return_value = [
        {
            'customer_id': 1,
            'customer_contact': '+6591234567',
            'customer_postal_code': '238123',
            'customer_street': 'Orchard Road',
            'customer_unit': '#01-01',
            'housing_type': 'HDB',
            'delivery_preferences': json.dumps({'time_slot': 'morning'}),
            'communication_preferences': json.dumps({'sms': True}),
            'latitude': 1.3521,
            'longitude': 103.8198,
            'created_at': '2025-10-15 10:00:00'
        }
    ]
    # Mock count result
    mock_db['cursor'].fetchone.side_effect = [None, {'total': 1}]
    
    response = client.get(
            '/customers?postal_code=238123',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'customers' in data
    assert len(data['customers']) > 0
    assert data['customers'][0]['customer_id'] == 1
    assert data['customers'][0]['housing_type'] == 'HDB'