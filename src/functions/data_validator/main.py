import json
import functions_framework
from google.cloud import pubsub_v1
from datetime import datetime
import time
from typing import Dict, Any, Optional
import logging
from functools import wraps
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Pub/Sub client
publisher = pubsub_v1.PublisherClient()
topic_path = None

# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # 1 minute window
MAX_REQUESTS_PER_WINDOW = 100
request_timestamps = []

# Validation rules
VALIDATION_RULES = {
    'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    'phone': r'^\+?[1-9]\d{1,14}$',
    'url': r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)$',
    'date': r'^\d{4}-\d{2}-\d{2}$',
    'timestamp': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?$'
}

def rate_limit(func):
    """Decorator to implement rate limiting."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        global request_timestamps
        current_time = time.time()
        
        # Remove timestamps older than the window
        request_timestamps = [ts for ts in request_timestamps 
                            if current_time - ts < RATE_LIMIT_WINDOW]
        
        if len(request_timestamps) >= MAX_REQUESTS_PER_WINDOW:
            logger.warning("Rate limit exceeded")
            return ('Rate limit exceeded. Please try again later.', 429)
        
        request_timestamps.append(current_time)
        return func(*args, **kwargs)
    return wrapper

def validate_field(field_name: str, value: Any, rules: Dict[str, Any]) -> Optional[str]:
    """Validate a field against its rules."""
    if field_name not in rules:
        return None
    
    field_rules = rules[field_name]
    
    # Check required field
    if field_rules.get('required', False) and value is None:
        return f"Field '{field_name}' is required"
    
    # Check type
    expected_type = field_rules.get('type')
    if expected_type and not isinstance(value, eval(expected_type)):
        return f"Field '{field_name}' must be of type {expected_type}"
    
    # Check format
    format_pattern = field_rules.get('format')
    if format_pattern and format_pattern in VALIDATION_RULES:
        if not re.match(VALIDATION_RULES[format_pattern], str(value)):
            return f"Field '{field_name}' has invalid format"
    
    # Check min/max for numbers
    if isinstance(value, (int, float)):
        if 'min' in field_rules and value < field_rules['min']:
            return f"Field '{field_name}' must be at least {field_rules['min']}"
        if 'max' in field_rules and value > field_rules['max']:
            return f"Field '{field_name}' must be at most {field_rules['max']}"
    
    # Check min/max length for strings
    if isinstance(value, str):
        if 'min_length' in field_rules and len(value) < field_rules['min_length']:
            return f"Field '{field_name}' must be at least {field_rules['min_length']} characters"
        if 'max_length' in field_rules and len(value) > field_rules['max_length']:
            return f"Field '{field_name}' must be at most {field_rules['max_length']} characters"
    
    return None

def transform_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform the data according to business rules."""
    transformed = data.copy()
    
    # Example transformations
    if 'email' in transformed:
        transformed['email'] = transformed['email'].lower().strip()
    
    if 'phone' in transformed:
        # Remove all non-digit characters
        transformed['phone'] = re.sub(r'\D', '', transformed['phone'])
    
    if 'timestamp' in transformed:
        try:
            # Convert to ISO format if not already
            if not re.match(VALIDATION_RULES['timestamp'], transformed['timestamp']):
                dt = datetime.fromisoformat(transformed['timestamp'].replace('Z', '+00:00'))
                transformed['timestamp'] = dt.isoformat()
        except ValueError:
            pass
    
    return transformed

@functions_framework.http
@rate_limit
def validate_data(request):
    """HTTP Cloud Function that validates incoming data and publishes to Pub/Sub."""
    global topic_path
    if topic_path is None:
        project_id = request.environ.get('PROJECT_ID')
        topic_path = publisher.topic_path(project_id, 'events-topic')

    # Parse request
    try:
        request_json = request.get_json(silent=True)
        if not request_json:
            logger.error("Invalid request: no JSON data")
            return ('Invalid request: no JSON data', 400)
    except Exception as e:
        logger.error(f"Error parsing JSON: {str(e)}")
        return ('Invalid JSON format', 400)

    # Define validation rules
    validation_rules = {
        'event_type': {
            'required': True,
            'type': 'str',
            'min_length': 1,
            'max_length': 50
        },
        'data': {
            'required': True,
            'type': 'dict'
        },
        'timestamp': {
            'required': False,
            'type': 'str',
            'format': 'timestamp'
        },
        'email': {
            'required': False,
            'type': 'str',
            'format': 'email'
        },
        'phone': {
            'required': False,
            'type': 'str',
            'format': 'phone'
        }
    }

    # Validate fields
    errors = []
    for field, value in request_json.items():
        error = validate_field(field, value, validation_rules)
        if error:
            errors.append(error)
    
    if errors:
        logger.warning(f"Validation errors: {errors}")
        return ({'errors': errors}, 400)

    # Transform data
    try:
        transformed_data = transform_data(request_json)
    except Exception as e:
        logger.error(f"Error transforming data: {str(e)}")
        return ('Error processing data', 500)

    # Add metadata
    event_data = {
        'event_id': str(datetime.now().timestamp()),
        'timestamp': datetime.now().isoformat(),
        'event_type': transformed_data['event_type'],
        'data': transformed_data['data'],
        'metadata': {
            'source': request.headers.get('X-Forwarded-For', 'unknown'),
            'user_agent': request.headers.get('User-Agent', 'unknown')
        }
    }

    # Publish to Pub/Sub
    try:
        future = publisher.publish(
            topic_path,
            json.dumps(event_data).encode('utf-8')
        )
        future.result()  # Wait for the publish to complete
        logger.info(f"Event published successfully: {event_data['event_id']}")
        return ({'message': 'Event published successfully', 'event_id': event_data['event_id']}, 200)
    except Exception as e:
        logger.error(f"Error publishing event: {str(e)}")
        return ({'error': f'Error publishing event: {str(e)}'}, 500)
