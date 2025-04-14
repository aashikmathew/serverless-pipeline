import json
import functions_framework
from google.cloud import pubsub_v1
from datetime import datetime

publisher = pubsub_v1.PublisherClient()
topic_path = None

@functions_framework.http
def validate_data(request):
    """HTTP Cloud Function that validates incoming data and publishes to Pub/Sub."""
    global topic_path
    if topic_path is None:
        project_id = request.environ.get('PROJECT_ID')
        topic_path = publisher.topic_path(project_id, 'events-topic')

    request_json = request.get_json(silent=True)
    
    if not request_json:
        return ('Invalid request: no JSON data', 400)

    # Validate required fields
    required_fields = ['event_type', 'data']
    for field in required_fields:
        if field not in request_json:
            return (f'Missing required field: {field}', 400)

    # Add metadata
    event_data = {
        'event_id': str(datetime.now().timestamp()),
        'timestamp': datetime.now().isoformat(),
        'event_type': request_json['event_type'],
        'data': request_json['data']
    }

    # Publish to Pub/Sub
    try:
        future = publisher.publish(
            topic_path,
            json.dumps(event_data).encode('utf-8')
        )
        future.result()  # Wait for the publish to complete
        return ('Event published successfully', 200)
    except Exception as e:
        return (f'Error publishing event: {str(e)}', 500)
