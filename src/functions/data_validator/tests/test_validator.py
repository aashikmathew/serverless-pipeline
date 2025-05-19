import sys
from unittest.mock import MagicMock
sys.modules['google.cloud.pubsub_v1'] = MagicMock()

from main import validate_data
import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import time

@pytest.fixture
def mock_request():
    """Create a mock request object."""
    mock = Mock()
    mock.environ = {"PROJECT_ID": "test-project"}
    mock.headers = {
        'X-Forwarded-For': '127.0.0.1',
        'User-Agent': 'test-agent'
    }
    return mock

@pytest.fixture
def mock_publisher():
    """Create a mock publisher client."""
    with patch('main.publisher') as mock:
        mock.topic_path.return_value = "projects/servless-pipeline/topics/events-topic"
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

def test_valid_request(mock_request, valid_data):
    mock_request.get_json.return_value = valid_data
    
    with patch('main.publisher.publish') as mock_publish:
        mock_future = MagicMock()
        mock_publish.return_value = mock_future
        mock_future.result.return_value = 'message-id'
        
        response, status_code = validate_data(mock_request)
        
        assert status_code == 200
        assert 'message' in response
        assert 'event_id' in response
        mock_publish.assert_called_once()

def test_missing_required_fields(mock_request):
    mock_request.get_json.return_value = {'data': {'key': 'value'}}
    
    response, status_code = validate_data(mock_request)
    
    assert status_code == 400
    assert 'errors' in response
    assert any('event_type' in error for error in response['errors'])

def test_invalid_email_format(mock_request, valid_data):
    valid_data['email'] = 'invalid-email'
    mock_request.get_json.return_value = valid_data
    
    response, status_code = validate_data(mock_request)
    
    assert status_code == 400
    assert 'errors' in response
    assert any('email' in error for error in response['errors'])

def test_invalid_phone_format(mock_request, valid_data):
    valid_data['phone'] = 'invalid-phone'
    mock_request.get_json.return_value = valid_data
    
    response, status_code = validate_data(mock_request)
    
    assert status_code == 400
    assert 'errors' in response
    assert any('phone' in error for error in response['errors'])

def test_invalid_timestamp_format(mock_request, valid_data):
    valid_data['timestamp'] = 'invalid-timestamp'
    mock_request.get_json.return_value = valid_data
    
    response, status_code = validate_data(mock_request)
    
    assert status_code == 400
    assert 'errors' in response
    assert any('timestamp' in error for error in response['errors'])

def test_rate_limiting(mock_request, valid_data):
    mock_request.get_json.return_value = valid_data
    
    # Make requests up to the limit
    for _ in range(100):
        response, status_code = validate_data(mock_request)
        assert status_code == 200
    
    # Next request should be rate limited
    response, status_code = validate_data(mock_request)
    assert status_code == 429
    assert 'Rate limit exceeded' in response

def test_data_transformation(mock_request, valid_data):
    valid_data['email'] = ' Test@Example.com '
    valid_data['phone'] = '+1 (234) 567-890'
    mock_request.get_json.return_value = valid_data
    
    with patch('main.publisher.publish') as mock_publish:
        mock_future = MagicMock()
        mock_publish.return_value = mock_future
        mock_future.result.return_value = 'message-id'
        
        response, status_code = validate_data(mock_request)
        
        assert status_code == 200
        # Verify the transformed data was published
        call_args = mock_publish.call_args[0]
        published_data = json.loads(call_args[1].decode('utf-8'))
        assert published_data['data']['email'] == 'test@example.com'
        assert published_data['data']['phone'] == '1234567890'

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

def test_validate_data_invalid_json():
    """Test the validate_data function with invalid JSON."""
    # Setup
    mock_request = Mock()
    mock_request.get_json = Mock(return_value=None)
    mock_request.environ = {"PROJECT_ID": "servless-pipeline"}
    
    # Execute
    response = validate_data(mock_request)
    
    # Assert
    assert response[1] == 400
    assert "Invalid request" in response[0]

def test_publish_error(mock_request, mock_publisher):
    """Test publishing error handling."""
    # Setup
    mock_publisher.publish.side_effect = Exception("Publish failed")
    
    # Execute
    response = validate_data(mock_request)
    
    # Assert
    assert response[1] == 500  # Check status code
    assert "Error publishing event" in response[0]  # Check error message 