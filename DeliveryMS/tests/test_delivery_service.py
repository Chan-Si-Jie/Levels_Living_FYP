# DeliveryMS/tests/test_delivery_service.py
import pytest
import json


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'ok'
    assert 'time' in data


def test_create_delivery_missing_order_id(client, mock_google_api):
    """Test creating delivery without orderId returns 422"""
    delivery_data = {
        "pickup": {"lat": 1.375645, "lng": 103.929573},
        "dropoff": {"lat": 1.44, "lng": 103.77}
    }
    
    response = client.post(
        '/deliveries',
        data=json.dumps(delivery_data),
        content_type='application/json'
    )
    
    assert response.status_code == 422
    data = response.get_json()
    assert 'orderId is required' in data['error']


def test_create_delivery_missing_dropoff(client, mock_google_api):
    """Test creating delivery without dropoff returns 422"""
    delivery_data = {
        "orderId": "ORD-001",
        "pickup": {"lat": 1.375645, "lng": 103.929573}
    }
    
    response = client.post(
        '/deliveries',
        data=json.dumps(delivery_data),
        content_type='application/json'
    )
    
    assert response.status_code == 422
    data = response.get_json()
    assert 'dropoff is required' in data['error']


def test_create_delivery_success(client, mock_google_api):
    """Test successful delivery creation"""
    delivery_data = {
        "orderId": "ORD-001",
        "pickup": {"lat": 1.375645, "lng": 103.929573},
        "dropoff": {"lat": 1.44, "lng": 103.77},
        "stops": [{"lat": 1.4291, "lng": 103.8360}],
        "driverId": "DRV-001"
    }
    
    response = client.post(
        '/deliveries',
        data=json.dumps(delivery_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'jobId' in data
    assert data['orderId'] == 'ORD-001'
    assert data['status'] == 'planned'
    assert 'route' in data
    assert data['route']['distanceMeters'] == 15000
    assert data['route']['duration'] == '1200s'


def test_create_delivery_with_postal_dropoff(client, mock_google_api):
    """Test creating delivery with postal code as dropoff"""
    delivery_data = {
        "orderId": "ORD-002",
        "dropoff": "460123"  # Postal code string
    }
    
    response = client.post(
        '/deliveries',
        data=json.dumps(delivery_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['orderId'] == 'ORD-002'
    assert data['dropoff']['lat'] == 1.3521
    assert data['dropoff']['lng'] == 103.8198


def test_get_delivery_not_found(client):
    """Test getting non-existent delivery returns 404"""
    response = client.get('/deliveries/nonexistent-job-id')
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'not found' in data['error']


def test_get_delivery_success(client, mock_google_api):
    """Test getting existing delivery"""
    # First create a delivery
    delivery_data = {
        "orderId": "ORD-003",
        "dropoff": {"lat": 1.44, "lng": 103.77}
    }
    
    create_response = client.post(
        '/deliveries',
        data=json.dumps(delivery_data),
        content_type='application/json'
    )
    
    job_id = create_response.get_json()['jobId']
    
    # Now get the delivery
    response = client.get(f'/deliveries/{job_id}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['jobId'] == job_id
    assert data['orderId'] == 'ORD-003'
    assert data['status'] == 'planned'


def test_update_delivery_status_invalid_status(client, mock_google_api):
    """Test updating delivery with invalid status returns 422"""
    # First create a delivery
    delivery_data = {
        "orderId": "ORD-004",
        "dropoff": {"lat": 1.44, "lng": 103.77}
    }
    
    create_response = client.post(
        '/deliveries',
        data=json.dumps(delivery_data),
        content_type='application/json'
    )
    
    job_id = create_response.get_json()['jobId']
    
    # Try to update with invalid status
    response = client.patch(
        f'/deliveries/{job_id}/status',
        data=json.dumps({"status": "invalid_status"}),
        content_type='application/json'
    )
    
    assert response.status_code == 422
    data = response.get_json()
    assert 'invalid status' in data['error'].lower()


def test_update_delivery_status_success(client, mock_google_api):
    """Test successful delivery status update"""
    # First create a delivery
    delivery_data = {
        "orderId": "ORD-005",
        "dropoff": {"lat": 1.44, "lng": 103.77}
    }
    
    create_response = client.post(
        '/deliveries',
        data=json.dumps(delivery_data),
        content_type='application/json'
    )
    
    job_id = create_response.get_json()['jobId']
    
    # Update status
    response = client.patch(
        f'/deliveries/{job_id}/status',
        data=json.dumps({"status": "en_route"}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'en_route'


def test_tracking_endpoint(client, mock_google_api):
    """Test public tracking endpoint"""
    # First create a delivery
    delivery_data = {
        "orderId": "ORD-006",
        "dropoff": {"lat": 1.44, "lng": 103.77},
        "driverId": "DRV-001"
    }
    
    create_response = client.post(
        '/deliveries',
        data=json.dumps(delivery_data),
        content_type='application/json'
    )
    
    job_id = create_response.get_json()['jobId']
    
    # Get tracking info
    response = client.get(f'/tracking/{job_id}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['jobId'] == job_id
    assert data['orderId'] == 'ORD-006'
    assert 'eta' in data
    assert 'polyline' in data
    assert 'distanceMeters' in data


def test_create_driver_missing_driver_id(client):
    """Test creating driver without driverId returns 422"""
    driver_data = {
        "name": "Test Driver",
        "vehicle": "Van"
    }
    
    response = client.post(
        '/drivers',
        data=json.dumps(driver_data),
        content_type='application/json'
    )
    
    assert response.status_code == 422
    data = response.get_json()
    assert 'driverId is required' in data['error']


def test_create_driver_success(client):
    """Test successful driver creation"""
    driver_data = {
        "driverId": "DRV-001",
        "name": "John Doe",
        "vehicle": "Van"
    }
    
    response = client.post(
        '/drivers',
        data=json.dumps(driver_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['driverId'] == 'DRV-001'
    assert data['name'] == 'John Doe'
    assert data['vehicle'] == 'Van'


def test_update_driver_location_not_found(client):
    """Test updating location for non-existent driver returns 404"""
    location_data = {
        "lat": 1.35,
        "lng": 103.82
    }
    
    response = client.patch(
        '/drivers/nonexistent-driver/location',
        data=json.dumps(location_data),
        content_type='application/json'
    )
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'not found' in data['error']


def test_update_driver_location_success(client):
    """Test successful driver location update"""
    # First create a driver
    driver_data = {
        "driverId": "DRV-002",
        "name": "Jane Smith"
    }
    
    client.post(
        '/drivers',
        data=json.dumps(driver_data),
        content_type='application/json'
    )
    
    # Update location
    location_data = {
        "lat": 1.35,
        "lng": 103.82
    }
    
    response = client.patch(
        '/drivers/DRV-002/location',
        data=json.dumps(location_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['last_location']['lat'] == 1.35
    assert data['last_location']['lng'] == 103.82


def test_geocode_missing_query(client):
    """Test geocode endpoint without query parameter returns 400"""
    response = client.get('/geocode')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'query parameter is required' in data['error']


def test_geocode_success(client, mock_google_api):
    """Test successful geocoding"""
    response = client.get('/geocode?query=460123')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['query'] == '460123'
    assert data['lat'] == 1.3521
    assert data['lng'] == 103.8198


def test_optimize_route_no_waypoints(client):
    """Test optimize route without waypoints returns 422"""
    route_data = {
        "waypoints": []
    }
    
    response = client.post(
        '/optimize-route',
        data=json.dumps(route_data),
        content_type='application/json'
    )
    
    assert response.status_code == 422
    data = response.get_json()
    assert 'No waypoints provided' in data['error']


def test_optimize_route_with_postal_codes(client, mock_google_api):
    """Test route optimization with postal codes"""
    route_data = {
        "waypoints": [
            {"order_id": "order-1", "postal_code": "460123", "sequence": 1},
            {"order_id": "order-2", "postal_code": "520234", "sequence": 2}
        ],
        "schedule_date": "2025-10-05"
    }
    
    response = client.post(
        '/optimize-route',
        data=json.dumps(route_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'route' in data
    assert data['route']['distance_meters'] == 15000
    assert data['route']['duration_seconds'] == 1200
    assert 'polyline' in data['route']
    assert 'waypoints' in data['route']


def test_optimize_route_legacy_format(client, mock_google_api):
    """Test route optimization with legacy format"""
    route_data = {
        "origin": {"lat": 1.375645, "lng": 103.929573},
        "destination": {"lat": 1.44, "lng": 103.77},
        "stops": [{"lat": 1.4291, "lng": 103.8360}]
    }
    
    response = client.post(
        '/optimize-route',
        data=json.dumps(route_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'routes' in data
    assert len(data['routes']) > 0


def test_tracking_with_driver_location(client, mock_google_api):
    """Test tracking endpoint shows driver location when available"""
    # Create a driver
    driver_data = {
        "driverId": "DRV-003",
        "name": "Test Driver"
    }
    
    client.post(
        '/drivers',
        data=json.dumps(driver_data),
        content_type='application/json'
    )
    
    # Update driver location
    location_data = {
        "lat": 1.36,
        "lng": 103.83
    }
    
    client.patch(
        '/drivers/DRV-003/location',
        data=json.dumps(location_data),
        content_type='application/json'
    )
    
    # Create delivery with driver
    delivery_data = {
        "orderId": "ORD-007",
        "dropoff": {"lat": 1.44, "lng": 103.77},
        "driverId": "DRV-003"
    }
    
    create_response = client.post(
        '/deliveries',
        data=json.dumps(delivery_data),
        content_type='application/json'
    )
    
    job_id = create_response.get_json()['jobId']
    
    # Get tracking with driver info
    response = client.get(f'/tracking/{job_id}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['driver'] is not None
    assert data['driver']['driverId'] == 'DRV-003'
    assert data['driver']['location']['lat'] == 1.36
    assert data['driver']['location']['lng'] == 103.83
