import pytest
import os
from unittest.mock import Mock, patch

# Set test environment variable
os.environ['PYTEST_CURRENT_TEST'] = 'True'

# Set environment variables for testing
os.environ['GCP_PROJECT'] = 'servless-pipeline' 

@pytest.fixture
def mock_request():
    """Create a mock request object with common attributes."""
    mock = Mock()
    mock.headers = {
        'X-Forwarded-For': '127.0.0.1',
        'User-Agent': 'test-agent'
    }
    mock.environ = {"PROJECT_ID": "test-project"}
    mock.remote_addr = '127.0.0.1'
    return mock

@pytest.fixture
def mock_publisher():
    """Create a mock publisher client."""
    with patch('main.publisher') as mock:
        mock_future = Mock()
        mock_future.result.return_value = 'message-id'
        mock.publish.return_value = mock_future
        mock.topic_path.return_value = 'test-topic'
        yield mock

@pytest.fixture
def valid_data():
    """Return a valid test data dictionary."""
    return {
        'event_type': 'test_event',
        'data': {'key': 'value'},
        'email': 'test@example.com',
        'phone': '+1234567890',
        'timestamp': '2024-02-14 12:00:00'
    } 