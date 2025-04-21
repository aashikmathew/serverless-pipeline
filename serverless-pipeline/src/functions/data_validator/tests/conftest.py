import os
import pytest
from unittest.mock import Mock, patch
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    # Store original environment variables
    original_env = {}
    for var in ['PYTEST_CURRENT_TEST', 'TEST_RATE_LIMIT']:
        if var in os.environ:
            original_env[var] = os.environ[var]
            
    # Set test environment variables
    os.environ['PYTEST_CURRENT_TEST'] = '1'
    
    yield
    
    # Restore original environment
    for var in ['PYTEST_CURRENT_TEST', 'TEST_RATE_LIMIT']:
        if var in original_env:
            os.environ[var] = original_env[var]
        elif var in os.environ:
            del os.environ[var]

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
    """Return a valid test data dictionary."""
    return {
        'event_type': 'test_event',
        'data': {'key': 'value'},
        'email': 'test@example.com',
        'phone': '+1234567890',
        'timestamp': '2024-02-14T12:00:00Z'
    } 