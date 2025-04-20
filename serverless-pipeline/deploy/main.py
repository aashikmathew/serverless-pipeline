import json
import functions_framework
from google.cloud import pubsub_v1
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Pub/Sub client
publisher = pubsub_v1.PublisherClient()
project_id = os.getenv('PROJECT_ID')
topic_path = publisher.topic_path(project_id, 'events-topic') if project_id else None

@functions_framework.http
def data_validator(request):
    """Cloud Function to validate incoming data."""
    try:
        # Get the request data
        request_json = request.get_json(silent=True)
        if not request_json:
            return ('Invalid JSON payload', 400)
            
        # Basic validation
        if not isinstance(request_json, dict):
            return ('Invalid data format: expected a JSON object', 400)
            
        # Check required fields
        required_fields = ['name', 'age', 'email']
        missing_fields = [field for field in required_fields if field not in request_json]
        if missing_fields:
            return (json.dumps({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400)
            
        # Validate email format
        if not isinstance(request_json['email'], str) or '@' not in request_json['email']:
            return (json.dumps({'error': 'Invalid email format'}), 400)
            
        # Validate age
        if not isinstance(request_json['age'], int) or request_json['age'] <= 0:
            return (json.dumps({'error': 'Age must be a positive integer'}), 400)
            
        # Publish to Pub/Sub
        try:
            future = publisher.publish(
                topic_path,
                json.dumps(request_json).encode('utf-8')
            )
            future.result()  # Wait for the publish to complete
            return (json.dumps({'message': 'Data validated and published successfully'}), 200)
        except Exception as e:
            logger.error(f"Error publishing to Pub/Sub: {str(e)}")
            return (json.dumps({'error': 'Failed to publish data'}), 500)
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return (json.dumps({'error': str(e)}), 500)
