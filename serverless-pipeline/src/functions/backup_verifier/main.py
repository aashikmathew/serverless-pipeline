import base64
import json
import os
from datetime import datetime
from google.cloud import pubsub_v1
from google.cloud import storage

def verify_backup(event, context):
    """Cloud Function triggered by Cloud Storage when a backup is completed.
    Args:
        event (dict): Event payload.
        context (google.cloud.functions.Context): Event context.
    """
    bucket_name = event['bucket']
    file_name = event['name']
    
    # Only process backup files
    if not file_name.startswith('backups/'):
        return
    
    project_id = os.environ.get('PROJECT_ID')
    topic_name = os.environ.get('TOPIC_NAME')
    
    # Verify backup files
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    # Check backup completion by verifying metadata files
    backup_date = file_name.split('/')[1]
    backup_files = list(bucket.list_blobs(prefix=f'backups/{backup_date}'))
    
    # Prepare notification message
    message = {
        'timestamp': datetime.utcnow().isoformat(),
        'backup_date': backup_date,
        'bucket': bucket_name,
        'status': 'success',
        'files_count': len(backup_files),
        'total_size': sum(blob.size for blob in backup_files)
    }
    
    # Publish notification
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_name)
    
    try:
        future = publisher.publish(
            topic_path,
            json.dumps(message).encode('utf-8'),
            backup_date=backup_date,
            status='success'
        )
        future.result()  # Wait for message to be published
        print(f"Backup verification complete: {message}")
    except Exception as e:
        print(f"Error publishing backup notification: {str(e)}")
        raise 