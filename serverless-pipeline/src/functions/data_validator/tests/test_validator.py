import pytest
from unittest.mock import Mock, patch
import json
import os
import sys
import time

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import validate_data, rate_limit, validate_field, transform_data, RATE_LIMIT

@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # Set the environment variable
    os.environ['PYTEST_CURRENT_TEST'] = '1'
    yield
    # Clean up after test
    if 'PYTEST_CURRENT_TEST' in os.environ:
        del os.environ['PYTEST_CURRENT_TEST']
    if 'TEST_RATE_LIMIT' in os.environ:
        del os.environ['TEST_RATE_LIMIT']

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
    mock.method = 'POST'
    mock.path = '/validate'
    return mock

@pytest.fixture
def mock_publisher():
    """Create a mock publisher client."""
    with patch('main.publisher') as mock:
        mock.topic_path.return_value = "projects/test-project/topics/events-topic"
        mock.publish.return_value.result.return_value = "test-event-id"
        yield mock

@pytest.fixture
def valid_data():
    """Create a valid data dictionary."""
    return {
        'event_type': 'test_event',
        'data': {'key': 'value'},
        'email': 'test@example.com',
        'phone': '+1234567890',
        'timestamp': '2024-02-14T12:00:00Z'
    }

@pytest.mark.timeout(5)
def test_valid_request(mock_request, valid_data, mock_publisher):
    """Test validation with valid data."""
    mock_request.get_json.return_value = valid_data.copy()
    response, status_code = validate_data(mock_request)
    assert status_code == 200
    assert 'message' in response
    assert 'event_id' in response

@pytest.mark.timeout(5)
def test_missing_required_fields(mock_request, valid_data):
    """Test validation with missing required fields."""
    for field in ['event_type', 'data', 'email', 'phone', 'timestamp']:
        test_data = valid_data.copy()
        del test_data[field]
        mock_request.get_json.return_value = test_data
        response, status_code = validate_data(mock_request)
        assert status_code == 400
        assert 'errors' in response
        assert any(f"{field} is required" in error for error in response['errors'])

@pytest.mark.timeout(5)
def test_invalid_email_format(mock_request, valid_data):
    """Test validation with invalid email format."""
    test_data = valid_data.copy()
    test_data['email'] = 'invalid-email'
    mock_request.get_json.return_value = test_data
    response, status_code = validate_data(mock_request)
    assert status_code == 400
    assert 'errors' in response
    assert any('email format is invalid' in error for error in response['errors'])

@pytest.mark.timeout(5)
def test_invalid_phone_format(mock_request, valid_data):
    """Test validation with invalid phone format."""
    test_data = valid_data.copy()
    test_data['phone'] = 'invalid-phone'
    mock_request.get_json.return_value = test_data
    response, status_code = validate_data(mock_request)
    assert status_code == 400
    assert 'errors' in response
    assert any('phone format is invalid' in error for error in response['errors'])

@pytest.mark.timeout(5)
def test_invalid_timestamp_format(mock_request, valid_data):
    """Test validation with invalid timestamp format."""
    test_data = valid_data.copy()
    test_data['timestamp'] = 'invalid-timestamp'
    mock_request.get_json.return_value = test_data
    response, status_code = validate_data(mock_request)
    assert status_code == 400
    assert 'error' in response
    assert 'Invalid timestamp format' in response['error']

@pytest.mark.timeout(5)
def test_rate_limiting(mock_request, valid_data, mock_publisher):
    """Test rate limiting functionality."""
    # Enable rate limiting for this test
    os.environ['TEST_RATE_LIMIT'] = '1'
    mock_request.get_json.return_value = valid_data.copy()
    
    # Reset rate limit dictionary
    from main import rate_limit_dict
    rate_limit_dict.clear()
    
    # Make requests up to the limit
    for _ in range(RATE_LIMIT):
        response, status_code = validate_data(mock_request)
        assert status_code == 200
    
    # Next request should be rate limited
    response, status_code = validate_data(mock_request)
    assert status_code == 429
    assert 'error' in response
    assert 'Rate limit exceeded' in response['error']

@pytest.mark.timeout(5)
def test_data_transformation(mock_request, valid_data, mock_publisher):
    """Test data transformation functionality."""
    # Reset rate limit dictionary
    from main import rate_limit_dict
    rate_limit_dict.clear()
    
    test_data = valid_data.copy()
    test_data['email'] = ' Test@Example.com '
    test_data['phone'] = '+1 (234) 567-890'
    mock_request.get_json.return_value = test_data
    response, status_code = validate_data(mock_request)
    assert status_code == 200
    assert 'message' in response
    assert 'event_id' in response

@pytest.mark.timeout(5)
def test_validate_field():
    """Test field validation function."""
    rules = {
        'name': {'required': True, 'type': 'str', 'min_length': 3},
        'age': {'required': True, 'type': 'int', 'min': 0, 'max': 120}
    }
    
    # Test valid field
    error = validate_field('name', 'John', rules)
    assert error is None
    
    # Test required field missing
    error = validate_field('name', None, rules)
    assert error == 'name is required'
    
    # Test invalid type
    error = validate_field('age', 'not a number', rules)
    assert error == 'age must be an integer'
    
    # Test min length
    error = validate_field('name', 'Jo', rules)
    assert error == 'name must be at least 3 characters long'
    
    # Test min/max value
    error = validate_field('age', -1, rules)
    assert error == 'age must be greater than or equal to 0'
    error = validate_field('age', 121, rules)
    assert error == 'age must be less than or equal to 120'

@pytest.mark.timeout(5)
def test_transform_data():
    """Test data transformation function."""
    data = {
        'email': ' Test@Example.com ',
        'phone': '+1 (234) 567-890',
        'timestamp': '2024-02-14T12:00:00Z'
    }
    
    transformed = transform_data(data)
    assert transformed['email'] == 'test@example.com'
    assert transformed['phone'] == '1234567890'
    assert transformed['timestamp'] == '2024-02-14T12:00:00Z'

@pytest.mark.timeout(5)
def test_validate_data_invalid_json(mock_request):
    """Test validation with invalid JSON."""
    # Reset rate limit dictionary
    from main import rate_limit_dict
    rate_limit_dict.clear()
    
    mock_request.get_json.side_effect = Exception('Invalid JSON')
    response, status_code = validate_data(mock_request)
    assert status_code == 400
    assert 'error' in response
    assert 'malformed JSON' in response['error']

@pytest.mark.timeout(5)
def test_publish_error(mock_request, valid_data, mock_publisher):
    """Test error handling during publish."""
    # Reset rate limit dictionary
    from main import rate_limit_dict
    rate_limit_dict.clear()
    
    mock_publisher.publish.side_effect = Exception('Publish error')
    mock_request.get_json.return_value = valid_data.copy()
    response, status_code = validate_data(mock_request)
    assert status_code == 500
    assert 'error' in response
    assert 'Error publishing event' in response['error'] 