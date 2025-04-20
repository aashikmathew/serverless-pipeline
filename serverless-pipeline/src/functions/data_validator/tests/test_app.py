import pytest
from unittest.mock import Mock, patch
import json
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import validate_data

@pytest.fixture
def mock_request():
    """Create a mock request object."""
    mock = Mock()
    mock.environ = {"PROJECT_ID": "test-project"}
    mock.headers = {
        'X-Forwarded-For': '127.0.0.1',
        'User-Agent': 'test-agent'
    }
    mock.remote_addr = '127.0.0.1'
    mock.get_json.return_value = {}  # Default empty JSON for health check
    return mock

@pytest.mark.timeout(5)
def test_health_check(mock_request):
    """Test the health check endpoint."""
    mock_request.path = '/health'
    mock_request.method = 'GET'
    mock_request.get_json.return_value = None  # No JSON data for health check
    
    # Reset rate limit dictionary
    from main import rate_limit_dict
    rate_limit_dict.clear()
    
    response, status_code = validate_data(mock_request)
    assert status_code == 200
    assert response == {'status': 'healthy'}

@pytest.mark.timeout(5)
def test_validate_endpoint(mock_request):
    """Test the validate endpoint with valid data."""
    mock_request.path = '/validate'
    mock_request.method = 'POST'
    mock_request.get_json.return_value = {
        'event_type': 'test_event',
        'data': {'key': 'value'},
        'email': 'test@example.com',
        'phone': '+1234567890',
        'timestamp': '2024-02-14T12:00:00Z'
    }
    
    # Reset rate limit dictionary
    from main import rate_limit_dict
    rate_limit_dict.clear()
    
    response, status_code = validate_data(mock_request)
    assert status_code == 200
    assert 'message' in response
    assert 'event_id' in response

@pytest.mark.timeout(5)
def test_validate_endpoint_invalid_data(mock_request):
    """Test the validate endpoint with invalid data."""
    mock_request.path = '/validate'
    mock_request.method = 'POST'
    mock_request.get_json.return_value = {
        'event_type': 'test_event',
        'data': {'key': 'value'},
        'email': 'invalid-email',
        'phone': 'invalid-phone',
        'timestamp': 'invalid-timestamp'
    }
    
    # Reset rate limit dictionary
    from main import rate_limit_dict
    rate_limit_dict.clear()
    
    response, status_code = validate_data(mock_request)
    assert status_code == 400
    assert 'errors' in response 