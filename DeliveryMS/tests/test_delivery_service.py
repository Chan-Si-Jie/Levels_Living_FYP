# DeliveryMS/tests/test_delivery_service.py
import pytest
import json
import os


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


# === NEW TESTS FOR 100% COVERAGE ===

def test_warehouse_fallback_no_env(client, monkeypatch, mock_google_api):
    """Test warehouse location falls back to default when env vars not set (line 54)"""
    monkeypatch.delenv('WAREHOUSE_LAT', raising=False)
    monkeypatch.delenv('WAREHOUSE_LNG', raising=False)
    
    # Call optimize-route which uses get_warehouse_waypoint
    route_data = {
        "waypoints": [
            {"order_id": "order-1", "postal_code": "460123", "sequence": 1}
        ]
    }
    
    response = client.post(
        '/optimize-route',
        data=json.dumps(route_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    # Default warehouse coordinates should be used


def test_normalize_waypoint_placeid(client):
    """Test normalize_waypoint with placeId format (lines 71-72)"""
    from app import normalize_waypoint
    
    waypoint = {"placeId": "ChIJN1t_tDeuEmsRUsoyG83frY4"}
    result = normalize_waypoint(waypoint)
    
    assert result == {"placeId": "ChIJN1t_tDeuEmsRUsoyG83frY4"}


def test_normalize_waypoint_string_address(client):
    """Test normalize_waypoint with string address format (lines 73-74)"""
    from app import normalize_waypoint
    
    waypoint = "10 Bayfront Ave, Singapore"
    result = normalize_waypoint(waypoint)
    
    assert result == {"location": {"address": "10 Bayfront Ave, Singapore"}}


def test_normalize_waypoint_invalid_format(client):
    """Test normalize_waypoint with invalid format raises ValueError (line 75)"""
    from app import normalize_waypoint
    
    with pytest.raises(ValueError, match="Bad waypoint format"):
        normalize_waypoint({"invalid": "format"})


def test_compute_route_no_api_key(client, monkeypatch):
    """Test compute_route without API key raises RuntimeError (line 81)"""
    from app import compute_route
    
    # Must reload app module to apply env change
    import app
    original_key = app.GOOGLE_API_KEY
    app.GOOGLE_API_KEY = None
    
    try:
        with pytest.raises(RuntimeError, match="GOOGLE_API_KEY not set"):
            compute_route({"lat": 1.0, "lng": 2.0}, {"lat": 3.0, "lng": 4.0}, [])
    finally:
        app.GOOGLE_API_KEY = original_key


def test_compute_route_no_routes_returned(client, mock_google_api, monkeypatch):
    """Test compute_route when Google returns no routes (line 104)"""
    from app import compute_route
    import requests
    
    # Mock requests.post to return empty routes
    original_post = requests.post
    def mock_post_no_routes(*args, **kwargs):
        class MockResponse:
            def json(self):
                return {"routes": []}
            def raise_for_status(self):
                pass
        return MockResponse()
    
    monkeypatch.setattr(requests, 'post', mock_post_no_routes)
    
    with pytest.raises(RuntimeError, match="No route returned from Google"):
        compute_route({"lat": 1.0, "lng": 2.0}, {"lat": 3.0, "lng": 4.0}, [])


def test_geocode_address_no_api_key(client, monkeypatch):
    """Test geocode_address without API key raises RuntimeError (line 112/414)"""
    from app import geocode_address
    
    monkeypatch.setenv('GOOGLE_API_KEY', '')
    
    with pytest.raises(RuntimeError, match="GOOGLE_API_KEY not set"):
        geocode_address("460123")


def test_geocode_address_failure(client, mock_google_api, monkeypatch):
    """Test geocode_address when geocoding fails (lines 122-123, 429-430)"""
    from app import geocode_address
    import requests
    
    # Mock requests.get to return failure status
    def mock_get_fail(*args, **kwargs):
        class MockResponse:
            def json(self):
                return {"status": "ZERO_RESULTS", "error_message": "No results found"}
            def raise_for_status(self):
                pass
        return MockResponse()
    
    monkeypatch.setattr(requests, 'get', mock_get_fail)
    
    with pytest.raises(RuntimeError, match="Geocode failed"):
        geocode_address("invalid address")


def test_to_latlng_numeric_values(client):
    """Test to_latlng with numeric lat/lng (lines 147-148)"""
    from app import to_latlng
    
    result = to_latlng({"lat": 1.23, "lng": 4.56})
    
    assert result == {"lat": 1.23, "lng": 4.56}


def test_to_latlng_invalid_numeric(client):
    """Test to_latlng with invalid numeric values (line 154)"""
    from app import to_latlng
    
    with pytest.raises(ValueError, match="lat/lng must be numeric"):
        to_latlng({"lat": "invalid", "lng": "invalid"})


def test_to_latlng_string_address(client, mock_google_api):
    """Test to_latlng with string address (lines 159-162)"""
    from app import to_latlng
    
    result = to_latlng("460123")
    
    assert result["lat"] == 1.3521
    assert result["lng"] == 103.8198


def test_to_latlng_invalid_format(client):
    """Test to_latlng with invalid format raises ValueError (line 162)"""
    from app import to_latlng
    
    with pytest.raises(ValueError, match="Expected"):
        to_latlng(123)  # Invalid type


def test_optimize_route_missing_postal_code(client):
    """Test optimize-route with missing postal_code (line 216)"""
    route_data = {
        "waypoints": [
            {"order_id": "order-1", "sequence": 1}  # Missing postal_code
        ]
    }
    
    response = client.post(
        '/optimize-route',
        data=json.dumps(route_data),
        content_type='application/json'
    )
    
    assert response.status_code == 422
    data = response.get_json()
    assert "Missing postal_code" in data['error']


def test_optimize_route_geocode_failure(client, mock_google_api, monkeypatch):
    """Test optimize-route when geocoding fails (lines 229-230)"""
    import requests
    
    # Mock geocode to fail
    def mock_get_fail(*args, **kwargs):
        raise Exception("Geocoding service error")
    
    monkeypatch.setattr(requests, 'get', mock_get_fail)
    
    route_data = {
        "waypoints": [
            {"order_id": "order-1", "postal_code": "460123", "sequence": 1}
        ]
    }
    
    response = client.post(
        '/optimize-route',
        data=json.dumps(route_data),
        content_type='application/json'
    )
    
    assert response.status_code == 422
    data = response.get_json()
    assert "Failed to geocode" in data['error']


def test_optimize_route_legacy_missing_origin(client):
    """Test optimize-route legacy format without origin (line 264)"""
    route_data = {
        "stops": [{"lat": 1.4291, "lng": 103.8360}]
        # Missing origin
    }
    
    response = client.post(
        '/optimize-route',
        data=json.dumps(route_data),
        content_type='application/json'
    )
    
    assert response.status_code == 422
    data = response.get_json()
    assert "origin is required" in data['error']


def test_create_delivery_invalid_dropoff(client):
    """Test create_delivery with invalid dropoff format (lines 297-298)"""
    delivery_data = {
        "orderId": "ORD-008",
        "dropoff": 12345  # Invalid format (not dict or string)
    }
    
    response = client.post(
        '/deliveries',
        data=json.dumps(delivery_data),
        content_type='application/json'
    )
    
    assert response.status_code == 422
    data = response.get_json()
    assert "Invalid dropoff" in data['error']


def test_create_delivery_invalid_stops(client):
    """Test create_delivery with invalid stops format (lines 306-307)"""
    delivery_data = {
        "orderId": "ORD-009",
        "dropoff": {"lat": 1.44, "lng": 103.77},
        "stops": [12345]  # Invalid stop format
    }
    
    response = client.post(
        '/deliveries',
        data=json.dumps(delivery_data),
        content_type='application/json'
    )
    
    assert response.status_code == 422
    data = response.get_json()
    assert "Invalid stop" in data['error']


def test_update_delivery_not_found(client):
    """Test update_delivery_status for non-existent delivery (line 348)"""
    response = client.patch(
        '/deliveries/nonexistent-job-id/status',
        data=json.dumps({"status": "en_route"}),
        content_type='application/json'
    )
    
    assert response.status_code == 404
    data = response.get_json()
    assert "not found" in data['error']


def test_tracking_not_found(client):
    """Test tracking endpoint for non-existent delivery (line 362)"""
    response = client.get('/tracking/nonexistent-job-id')
    
    assert response.status_code == 404
    data = response.get_json()
    assert "not found" in data['error']


def test_update_driver_location_invalid_lat_lng(client):
    """Test update driver location with invalid lat/lng (lines 451)"""
    # First create a driver
    driver_data = {
        "driverId": "DRV-004",
        "name": "Test Driver"
    }
    
    client.post(
        '/drivers',
        data=json.dumps(driver_data),
        content_type='application/json'
    )
    
    # Try to update with invalid lat/lng
    location_data = {
        "lat": "invalid",
        "lng": 103.82
    }
    
    response = client.patch(
        '/drivers/DRV-004/location',
        data=json.dumps(location_data),
        content_type='application/json'
    )
    
    assert response.status_code == 422
    data = response.get_json()
    assert "lat and lng required" in data['error']


def test_geocode_exception_handling(client, mock_google_api, monkeypatch):
    """Test geocode endpoint exception handling (lines 461-468)"""
    import requests
    
    # Mock geocode_address to raise exception
    def mock_get_fail(*args, **kwargs):
        raise Exception("Service unavailable")
    
    monkeypatch.setattr(requests, 'get', mock_get_fail)
    
    response = client.get('/geocode?query=460123')
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data


def test_testing_endpoint_no_api_key(client, monkeypatch):
    """Test /testing endpoint when no API key configured (lines 464-468)"""
    import app
    
    # Save originals
    original_api_key = app.GOOGLE_API_KEY
    original_js_key = os.getenv('GOOGLE_JS_KEY')
    
    # Set both to None/empty
    app.GOOGLE_API_KEY = None
    monkeypatch.delenv('GOOGLE_JS_KEY', raising=False)
    
    try:
        response = client.get('/testing')
        
        assert response.status_code == 500
        data = response.get_json()
        assert "Google API key not configured" in data['error']
    finally:
        # Restore
        app.GOOGLE_API_KEY = original_api_key


def test_testing_endpoint_success(client):
    """Test /testing endpoint with API key configured"""
    # Use existing GOOGLE_API_KEY from fixture
    response = client.get('/testing')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'google_api_key' in data
    assert 'endpoints' in data


def test_error_handler_http_exception(client):
    """Test error handler with HTTPException (lines 159-162)"""
    # Trigger 404 which is an HTTPException
    response = client.get('/nonexistent-endpoint')
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data


def test_error_handler_generic_exception(client, monkeypatch):
    """Test error handler with generic Exception (line 164)"""
    import app
    
    # Mock a function to raise an exception
    def mock_health():
        raise Exception("Test exception")
    
    # Replace health endpoint temporarily
    original_health = app.health
    app.app.view_functions['health'] = mock_health
    
    try:
        response = client.get('/health')
        
        assert response.status_code == 500
        data = response.get_json()
        assert 'Test exception' in data['error']
    finally:
        app.app.view_functions['health'] = original_health
