import os
import sys
import pytest
from unittest.mock import Mock, patch

# Add the necessary directories to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.dirname(parent_dir))

# Set test environment variables
os.environ['GCP_PROJECT'] = 'servless-pipeline'
os.environ['PYTEST_CURRENT_TEST'] = '1'

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ["PYTEST_CURRENT_TEST"] = "1"
    yield
    if "PYTEST_CURRENT_TEST" in os.environ:
        del os.environ["PYTEST_CURRENT_TEST"]

@pytest.fixture
def mock_request():
    """Create a mock request object."""
    request = Mock()
    request.method = 'POST'
    request.headers = {}
    request.remote_addr = '127.0.0.1'
    request.get_json.return_value = {}
    return request

@pytest.fixture
def mock_publisher():
    """Create a mock publisher object."""
    with patch('google.cloud.pubsub_v1.PublisherClient') as mock:
        mock.return_value.topic_path.return_value = "projects/servless-pipeline/topics/events-topic"
        mock.return_value.publish.return_value.result.return_value = "test-event-id"
        yield mock.return_value

@pytest.fixture
def valid_data():
    """Create valid test data."""
    return {
        'event_type': 'test_event',
        'data': {'key': 'value'},
        'email': 'test@example.com',
        'phone': '+1234567890',
        'timestamp': '2024-02-14T12:00:00'
    } 