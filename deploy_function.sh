#!/bin/bash

# Create the function directory if it doesn't exist
mkdir -p src/functions/data_validator

# Create main.py
cat > src/functions/data_validator/main.py << 'PYTHON'
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
PYTHON

# Create requirements.txt
cat > src/functions/data_validator/requirements.txt << 'REQUIREMENTS'
functions-framework==3.*
google-cloud-pubsub==2.*
flask==2.*
REQUIREMENTS

# Install dependencies and create zip
cd src/functions/data_validator
pip install -r requirements.txt -t .
zip -r ../data-validator.zip .

# Upload to Cloud Storage
gsutil cp ../data-validator.zip gs://servless-pipeline-static-assets/functions/

# Deploy the function
gcloud functions deploy data-validator \
  --runtime python39 \
  --trigger-http \
  --entry-point validate_data \
  --source gs://servless-pipeline-static-assets/functions/data-validator.zip \
  --project servless-pipeline \
  --region us-central1
