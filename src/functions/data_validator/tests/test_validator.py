import pytest
from unittest.mock import Mock, patch
import json
from src.functions.data_validator.main import validate_data

@pytest.fixture
def mock_request():
    """Create a mock request object."""
    mock = Mock()
    mock.get_json = Mock(return_value={
        "event_type": "test_event",
        "data": "test_data"
    })
    mock.environ = {"PROJECT_ID": "servless-pipeline"}
    return mock

@pytest.fixture
def mock_publisher():
    """Create a mock publisher client."""
    with patch('src.functions.data_validator.main.publisher') as mock:
        mock.topic_path.return_value = "projects/servless-pipeline/topics/events-topic"
        yield mock

def test_validate_data_valid_request(mock_request, mock_publisher):
    """Test the validate_data function with a valid request."""
    # Setup
    mock_publisher.publish.return_value.result.return_value = None
    response = validate_data(mock_request)
    
    # Assert
    assert response[1] == 200  # Check status code
    assert "successfully" in response[0]  # Check message

def test_validate_data_missing_field():
    """Test the validate_data function with missing required field."""
    # Setup
    mock_request = Mock()
    mock_request.get_json = Mock(return_value={"event_type": "test"})  # Missing 'data' field
    mock_request.environ = {"PROJECT_ID": "servless-pipeline"}
    
    # Execute
    response = validate_data(mock_request)
    
    # Assert
    assert response[1] == 400  # Check status code
    assert "Missing required field" in response[0]  # Check error message

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