import json
import functions_framework
from google.cloud import pubsub_v1
import logging
import os
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Pub/Sub client
publisher = pubsub_v1.PublisherClient()
project_id = 'servless-pipeline'  # Hardcoding the project ID since we know it
topic_path = publisher.topic_path(project_id, 'events-topic')

def validate_email(email):
    """Validate email format using regex."""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_regex, email))

@functions_framework.http
def data_validator(request):
    """Cloud Function to validate incoming data."""
    try:
        # Get the request data
        request_json = request.get_json(silent=True)
        if not request_json:
            return (json.dumps({
                'error': 'Invalid JSON payload',
                'code': 'INVALID_JSON',
                'message': 'The request body must be a valid JSON object'
            }), 400)
            
        # Basic validation
        if not isinstance(request_json, dict):
            return (json.dumps({
                'error': 'Invalid data format',
                'code': 'INVALID_FORMAT',
                'message': 'Expected a JSON object'
            }), 400)
            
        # Check required fields
        required_fields = ['name', 'age', 'email']
        missing_fields = [field for field in required_fields if field not in request_json]
        if missing_fields:
            return (json.dumps({
                'error': 'Missing required fields',
                'code': 'MISSING_FIELDS',
                'message': f'Required fields missing: {", ".join(missing_fields)}',
                'missing_fields': missing_fields
            }), 400)
            
        # Validate name
        if not isinstance(request_json['name'], str) or len(request_json['name'].strip()) == 0:
            return (json.dumps({
                'error': 'Invalid name',
                'code': 'INVALID_NAME',
                'message': 'Name must be a non-empty string'
            }), 400)
            
        # Validate email format
        if not isinstance(request_json['email'], str) or not validate_email(request_json['email']):
            return (json.dumps({
                'error': 'Invalid email',
                'code': 'INVALID_EMAIL',
                'message': 'Email must be a valid email address (e.g., user@example.com)'
            }), 400)
            
        # Validate age
        if not isinstance(request_json['age'], int):
            return (json.dumps({
                'error': 'Invalid age type',
                'code': 'INVALID_AGE_TYPE',
                'message': 'Age must be an integer'
            }), 400)
            
        if request_json['age'] <= 0:
            return (json.dumps({
                'error': 'Invalid age value',
                'code': 'INVALID_AGE_VALUE',
                'message': 'Age must be a positive integer'
            }), 400)
            
        # Publish to Pub/Sub
        try:
            future = publisher.publish(
                topic_path,
                json.dumps(request_json).encode('utf-8')
            )
            future.result()  # Wait for the publish to complete
            return (json.dumps({
                'message': 'Data validated and published successfully',
                'code': 'SUCCESS',
                'data': request_json
            }), 200)
        except Exception as e:
            logger.error(f"Error publishing to Pub/Sub: {str(e)}")
            return (json.dumps({
                'error': 'Publishing failed',
                'code': 'PUBLISH_ERROR',
                'message': 'Failed to publish data to the queue'
            }), 500)
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return (json.dumps({
            'error': 'Server error',
            'code': 'SERVER_ERROR',
            'message': str(e)
        }), 500)
