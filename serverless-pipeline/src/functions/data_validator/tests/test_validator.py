import pytest
from unittest.mock import Mock, patch
import json
import os
import sys
import time

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import validate_data, rate_limit, validate_field, transform_data

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
    return mock

@pytest.fixture
def mock_publisher():
    """Create a mock publisher client."""
    with patch('main.publisher') as mock:
        mock.topic_path.return_value = "projects/servless-pipeline/topics/events-topic"
        mock.publish.return_value.result.return_value = "test-event-id"
        yield mock

@pytest.fixture
def valid_data():
    return {
        'event_type': 'test_event',
        'data': {'key': 'value'},
        'email': 'test@example.com',
        'phone': '+1234567890',
        'timestamp': '2024-02-14T12:00:00Z'
    }

@pytest.mark.timeout(5)  # Add timeout to prevent hanging
def test_valid_request(mock_request, mock_publisher, valid_data):
    mock_request.get_json.return_value = valid_data
    
    # Reset rate limit dictionary
    from main import rate_limit_dict
    rate_limit_dict.clear()
    
    response, status_code = validate_data(mock_request)
    
    assert status_code == 200
    assert 'message' in response
    assert 'event_id' in response

@pytest.mark.timeout(5)
def test_missing_required_fields(mock_request):
    mock_request.get_json.return_value = {'data': {'key': 'value'}}
    
    # Reset rate limit dictionary
    from main import rate_limit_dict
    rate_limit_dict.clear()
    
    response, status_code = validate_data(mock_request)
    
    assert status_code == 400
    assert 'errors' in response
    assert any('event_type' in error for error in response['errors'])

@pytest.mark.timeout(5)
def test_invalid_email_format(mock_request, valid_data):
    valid_data['email'] = 'invalid-email'
    mock_request.get_json.return_value = valid_data
    
    # Reset rate limit dictionary
    from main import rate_limit_dict
    rate_limit_dict.clear()
    
    response, status_code = validate_data(mock_request)
    
    assert status_code == 400
    assert 'errors' in response
    assert any('email' in error for error in response['errors'])

@pytest.mark.timeout(5)
def test_invalid_phone_format(mock_request, valid_data):
    valid_data['phone'] = 'invalid-phone'
    mock_request.get_json.return_value = valid_data
    
    # Reset rate limit dictionary
    from main import rate_limit_dict
    rate_limit_dict.clear()
    
    response, status_code = validate_data(mock_request)
    
    assert status_code == 400
    assert 'errors' in response
    assert any('phone' in error for error in response['errors'])

@pytest.mark.timeout(5)
def test_invalid_timestamp_format(mock_request, valid_data):
    valid_data['timestamp'] = 'invalid-timestamp'
    mock_request.get_json.return_value = valid_data
    
    # Reset rate limit dictionary
    from main import rate_limit_dict
    rate_limit_dict.clear()
    
    response, status_code = validate_data(mock_request)
    
    assert status_code == 400
    assert 'errors' in response
    assert any('timestamp' in error for error in response['errors'])

@pytest.mark.timeout(5)
def test_rate_limiting(mock_request, valid_data, mock_publisher):
    mock_request.get_json.return_value = valid_data
    
    # Reset rate limit dictionary
    from main import rate_limit_dict
    rate_limit_dict.clear()
    
    # Make requests up to the limit
    for _ in range(100):
        response, status_code = validate_data(mock_request)
        assert status_code == 200
    
    # Next request should be rate limited
    response, status_code = validate_data(mock_request)
    assert status_code == 429
    assert 'error' in response
    assert 'Rate limit exceeded' in response['error']

@pytest.mark.timeout(5)
def test_data_transformation(mock_request, valid_data, mock_publisher):
    valid_data['email'] = ' Test@Example.com '
    valid_data['phone'] = '+1 (234) 567-890'
    mock_request.get_json.return_value = valid_data
    
    # Reset rate limit dictionary
    from main import rate_limit_dict
    rate_limit_dict.clear()
    
    response, status_code = validate_data(mock_request)
    
    assert status_code == 200
    # Verify the transformed data
    assert 'data' in response
    published_data = response['data']['data']
    assert published_data['email'] == 'test@example.com'
    assert published_data['phone'] == '1234567890'

@pytest.mark.timeout(5)
def test_validate_field():
    rules = {
        'name': {'required': True, 'type': 'str', 'min_length': 2},
        'age': {'required': True, 'type': 'int', 'min': 0, 'max': 120}
    }
    
    # Test valid field
    assert validate_field('name', 'John', rules) is None
    
    # Test missing required field
    assert validate_field('name', None, rules) is not None
    
    # Test invalid type
    assert validate_field('age', 'not a number', rules) is not None
    
    # Test min/max validation
    assert validate_field('age', -1, rules) is not None
    assert validate_field('age', 121, rules) is not None

@pytest.mark.timeout(5)
def test_transform_data():
    data = {
        'email': ' Test@Example.com ',
        'phone': '+1 (234) 567-890',
        'timestamp': '2024-02-14 12:00:00'
    }
    
    transformed = transform_data(data)
    
    assert transformed['email'] == 'test@example.com'
    assert transformed['phone'] == '1234567890'
    assert transformed['timestamp'].startswith('2024-02-14T12:00:00')

@pytest.mark.timeout(5)
def test_validate_data_invalid_json(mock_request):
    mock_request.get_json.side_effect = Exception("Invalid JSON")
    
    # Reset rate limit dictionary
    from main import rate_limit_dict
    rate_limit_dict.clear()
    
    response, status_code = validate_data(mock_request)
    
    assert status_code == 400
    assert 'error' in response
    assert 'Invalid request' in response['error']

@pytest.mark.timeout(5)
def test_publish_error(mock_request, valid_data):
    mock_request.get_json.return_value = valid_data
    
    # Reset rate limit dictionary
    from main import rate_limit_dict
    rate_limit_dict.clear()
    
    # Mock the publisher to raise an exception
    with patch('main.publisher') as mock_publisher:
        mock_publisher.topic_path.return_value = "projects/servless-pipeline/topics/events-topic"
        mock_publisher.publish.side_effect = Exception("Publish failed")
        
        # Set environment variable to test error handling
        with patch.dict(os.environ, {'PYTEST_CURRENT_TEST': '1', 'TEST_PUBLISH_ERROR': '1'}):
            response, status_code = validate_data(mock_request)
            
            assert status_code == 500
            assert 'error' in response
            assert 'Error publishing event' in response['error'] 