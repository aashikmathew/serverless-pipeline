import pytest
from main import data_validator, validate_email
from unittest.mock import Mock, patch

def test_validate_email():
    assert validate_email("test@example.com") == True
    assert validate_email("invalid-email") == False
    assert validate_email("test@.com") == False
    assert validate_email("@example.com") == False

def test_data_validator_missing_fields():
    request = Mock()
    request.get_json = Mock(return_value={"name": "Test"})
    response, status_code = data_validator(request)
    assert status_code == 400
    assert "missing_fields" in response

def test_data_validator_invalid_email():
    request = Mock()
    request.get_json = Mock(return_value={
        "name": "Test",
        "email": "invalid-email",
        "age": 25
    })
    response, status_code = data_validator(request)
    assert status_code == 400
    assert "INVALID_EMAIL" in response

def test_data_validator_invalid_age():
    request = Mock()
    request.get_json = Mock(return_value={
        "name": "Test",
        "email": "test@example.com",
        "age": -1
    })
    response, status_code = data_validator(request)
    assert status_code == 400
    assert "INVALID_AGE_VALUE" in response

def test_data_validator_valid_data():
    request = Mock()
    request.get_json = Mock(return_value={
        "name": "Test User",
        "email": "test@example.com",
        "age": 25
    })
    response, status_code = data_validator(request)
    assert status_code == 200
    assert "SUCCESS" in response

@pytest.fixture
def mock_request():
    mock = Mock()
    mock.headers = {'X-Forwarded-For': '127.0.0.1'}
    mock.environ = {'PROJECT_ID': 'test-project'}
    return mock

def test_validate_data_success(mock_request):
    # Test data
    test_data = {
        'event_type': 'test_event',
        'data': {'key': 'value'},
        'email': 'test@example.com',
        'phone': '+1234567890',
        'timestamp': '2024-02-14 12:00:00'
    }
    mock_request.get_json.return_value = test_data

    # Mock publisher
    with patch('main.publisher') as mock_publisher:
        mock_future = Mock()
        mock_future.result.return_value = 'message-id'
        mock_publisher.publish.return_value = mock_future
        mock_publisher.topic_path.return_value = 'test-topic'

        # Call function
        response, status_code = validate_data(mock_request)

        # Assertions
        assert status_code == 200
        assert 'message' in response
        assert 'event_id' in response
        mock_publisher.publish.assert_called_once() 