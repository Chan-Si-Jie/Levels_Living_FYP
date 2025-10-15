# DeliveryMS/tests/conftest.py
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
def mock_google_api(mocker):
    """Mock Google API requests (Routes API and Geocoding API)"""
    # Mock the requests.post for Routes API
    mock_routes_response = mocker.MagicMock()
    mock_routes_response.json.return_value = {
        "routes": [{
            "distanceMeters": 15000,
            "duration": "1200s",
            "polyline": {
                "encodedPolyline": "test_encoded_polyline_string"
            },
            "optimizedIntermediateWaypointIndex": [0, 1, 2]
        }]
    }
    mock_routes_response.raise_for_status.return_value = None
    
    # Mock the requests.get for Geocoding API
    mock_geocode_response = mocker.MagicMock()
    mock_geocode_response.json.return_value = {
        "status": "OK",
        "results": [{
            "geometry": {
                "location": {
                    "lat": 1.3521,
                    "lng": 103.8198
                }
            },
            "formatted_address": "123 Test Street, Singapore 123456",
            "place_id": "test_place_id"
        }]
    }
    mock_geocode_response.raise_for_status.return_value = None
    
    # Use side_effect to return different responses based on the request type
    def request_side_effect(method, url, *args, **kwargs):
        if "routes.googleapis.com" in url:
            return mock_routes_response
        elif "geocode" in url:
            return mock_geocode_response
        return mocker.MagicMock()
    
    mocker.patch('requests.request', side_effect=request_side_effect)
    mocker.patch('requests.post', return_value=mock_routes_response)
    mocker.patch('requests.get', return_value=mock_geocode_response)
    
    return {
        'routes': mock_routes_response,
        'geocode': mock_geocode_response
    }


@pytest.fixture(autouse=True)
def clear_in_memory_stores():
    """Clear in-memory stores before each test"""
    from app import JOBS, DRIVERS
    JOBS.clear()
    DRIVERS.clear()
    yield
    JOBS.clear()
    DRIVERS.clear()
