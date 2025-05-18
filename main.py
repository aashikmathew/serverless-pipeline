import functions_framework
import json
import os
from google.cloud import pubsub_v1

@functions_framework.http
def validate_data(request):
    """HTTP Cloud Function that validates incoming data.
    
    Args:
        request (flask.Request): The request object.
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
    """
    try:
        # Get request data
        request_json = request.get_json(silent=True)
        if not request_json:
            return 'No data provided', 400

        # Validate required fields
        required_fields = ['event_id', 'timestamp', 'event_type', 'data']
        missing_fields = [field for field in required_fields if field not in request_json]
        if missing_fields:
            return f'Missing required fields: {", ".join(missing_fields)}', 400

        # Validate data types
        if not isinstance(request_json['event_id'], str):
            return 'event_id must be a string', 400
        if not isinstance(request_json['timestamp'], str):
            return 'timestamp must be a string', 400
        if not isinstance(request_json['event_type'], str):
            return 'event_type must be a string', 400

        # Publish validated data to Pub/Sub
        project_id = os.environ.get('PROJECT_ID')
        topic_name = 'events-topic'
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_name)

        data = json.dumps(request_json).encode('utf-8')
        future = publisher.publish(topic_path, data)
        message_id = future.result()

        return {
            'message': 'Data validated and published successfully',
            'message_id': message_id
        }, 200

    except Exception as e:
        return str(e), 500 