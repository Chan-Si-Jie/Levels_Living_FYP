# DeliveryMS/tests/conftest.py
import pytest
import sys
import os

# Add parent directory to path to import app module
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Set environment variables BEFORE importing app
os.environ['GOOGLE_API_KEY'] = 'test-api-key'
os.environ['WAREHOUSE_LAT'] = '1.375645'
os.environ['WAREHOUSE_LONG'] = '103.929573'

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
    
    # Mock Routes API response
    def mock_routes_post(*args, **kwargs):
        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {
            "routes": [{
                "distanceMeters": 15000,
                "duration": "1200s",
                "polyline": {
                    "encodedPolyline": "test_encoded_polyline_string"
                },
                "optimizedIntermediateWaypointIndex": [0, 1, 2]
            }]
        }
        mock_response.raise_for_status.return_value = None
        return mock_response
    
    # Mock Geocoding API response
    def mock_geocode_get(*args, **kwargs):
        mock_response = mocker.MagicMock()
        mock_response.json.return_value = {
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
        mock_response.raise_for_status.return_value = None
        return mock_response
    
    # Patch requests at the app module level (where they're imported)
    mocker.patch('app.requests.post', side_effect=mock_routes_post)
    mocker.patch('app.requests.get', side_effect=mock_geocode_get)
    
    return {
        'routes': mock_routes_post,
        'geocode': mock_geocode_get
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
