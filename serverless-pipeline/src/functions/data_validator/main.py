import json
import re
import time
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List
from google.cloud import pubsub_v1
import functions_framework
from flask import Request
import os
from functools import lru_cache

# Initialize Pub/Sub client with timeout
publisher = pubsub_v1.PublisherClient()
PUBSUB_TIMEOUT = 10  # seconds

# Rate limiting configuration
RATE_LIMIT = 100  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds
rate_limit_dict = {}

def cleanup_old_entries():
    """Clean up entries older than the rate limit window."""
    current_time = time.time()
    for ip in list(rate_limit_dict.keys()):
        rate_limit_dict[ip] = [t for t in rate_limit_dict[ip] if t > current_time - RATE_LIMIT_WINDOW]
        if not rate_limit_dict[ip]:
            del rate_limit_dict[ip]

def rate_limit(ip: str) -> bool:
    """
    Implement rate limiting based on IP address.
    Returns True if rate limit is exceeded, False otherwise.
    """
    if os.getenv('PYTEST_CURRENT_TEST') and not os.getenv('TEST_RATE_LIMIT'):
        return False
        
    current_time = time.time()
    
    # Clean up old entries periodically
    if len(rate_limit_dict) > 1000:  # Cleanup when dictionary gets too large
        cleanup_old_entries()
    
    # Get request count for this IP
    requests = len(rate_limit_dict.get(ip, []))
    
    if requests >= RATE_LIMIT:
        return True
        
    # Add new request timestamp
    if ip not in rate_limit_dict:
        rate_limit_dict[ip] = []
    rate_limit_dict[ip].append(current_time)
    
    return False

@lru_cache(maxsize=1000)
def compile_regex(pattern: str) -> re.Pattern:
    """Compile and cache regex patterns."""
    return re.compile(pattern)

def validate_field(field_name: str, value: Any, rules: Dict) -> Optional[str]:
    """
    Validate a single field according to the provided rules.
    Returns error message if validation fails, None otherwise.
    """
    field_rules = rules.get(field_name, {})
    
    # Check required
    if field_rules.get('required', False) and value is None:
        return f"{field_name} is required"
        
    if value is None:
        return None
        
    # Check type
    expected_type = field_rules.get('type')
    if expected_type == 'str' and not isinstance(value, str):
        return f"{field_name} must be a string"
    elif expected_type == 'int' and not isinstance(value, int):
        return f"{field_name} must be an integer"
        
    # Check string length
    if isinstance(value, str):
        min_length = field_rules.get('min_length', 0)
        if len(value) < min_length:
            return f"{field_name} must be at least {min_length} characters long"
            
    # Check number range
    if isinstance(value, (int, float)):
        min_val = field_rules.get('min')
        max_val = field_rules.get('max')
        if min_val is not None and value < min_val:
            return f"{field_name} must be greater than or equal to {min_val}"
        if max_val is not None and value > max_val:
            return f"{field_name} must be less than or equal to {max_val}"
            
    return None

def transform_data(data: Dict) -> Dict:
    """Transform and normalize data fields."""
    transformed = data.copy()
    
    # Transform email: strip whitespace and convert to lowercase
    if 'email' in transformed:
        transformed['email'] = transformed['email'].strip().lower()
    
    # Transform phone: remove all non-digit characters
    if 'phone' in transformed:
        transformed['phone'] = ''.join(filter(str.isdigit, transformed['phone']))
    
    return transformed

@functions_framework.http
def data_validator(request: Request) -> Tuple[Dict, int]:
    """
    Validate incoming event data and publish to Pub/Sub if valid.
    """
    start_time = time.time()
    
    # Handle health check endpoint
    if request.method == 'GET' and getattr(request, 'path', '') == '/health':
        return {'status': 'healthy'}, 200
    
    # Get client IP for rate limiting
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    
    # Check rate limit
    if rate_limit(client_ip):
        return {"error": "Rate limit exceeded"}, 429
        
    # Parse request data
    try:
        data = request.get_json()
        if not data:
            return {"error": "Invalid request: no data provided"}, 400
    except Exception:
        return {"error": "Invalid request: malformed JSON"}, 400
        
    # Validation rules
    rules = {
        'event_type': {'required': True, 'type': 'str'},
        'data': {'required': True},
        'email': {'required': True, 'type': 'str', 'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'},
        'phone': {'required': True, 'type': 'str', 'pattern': r'^\+?[\d\s\-\(\)]+$'},
        'timestamp': {'required': True, 'type': 'str'}
    }
    
    # Transform data
    try:
        transformed_data = transform_data(data)
    except ValueError as e:
        return {"error": str(e)}, 400
    
    # Validate fields
    errors = []
    for field, field_rules in rules.items():
        if field_rules.get('required', False) and field not in transformed_data:
            errors.append(f"{field} is required")
            continue
            
        if field in transformed_data:
            value = transformed_data[field]
            
            # Basic field validation
            error = validate_field(field, value, rules)
            if error:
                errors.append(error)
                continue
                
            # Special handling for timestamp format
            if field == 'timestamp':
                if not compile_regex(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$').match(value):
                    return {"error": "Invalid timestamp format"}, 400
                continue
                
            # Pattern validation for strings
            if isinstance(value, str) and 'pattern' in field_rules:
                pattern = field_rules['pattern']
                if not compile_regex(pattern).match(value):
                    errors.append(f"{field} format is invalid")
                    
    if errors:
        return {"errors": errors}, 400
        
    # Publish to Pub/Sub with timeout
    try:
        topic_path = publisher.topic_path(
            request.environ.get("PROJECT_ID", "servless-pipeline"),
            "events-topic"
        )
        
        # Prepare message data
        message_data = {
            "data": transformed_data,
            "metadata": {
                "ip": client_ip,
                "user_agent": request.headers.get('User-Agent'),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Publish message with timeout
        future = publisher.publish(
            topic_path,
            json.dumps(message_data).encode('utf-8')
        )
        
        try:
            event_id = future.result(timeout=PUBSUB_TIMEOUT)
        except Exception as e:
            return {"error": f"Failed to publish message: {str(e)}"}, 500
        
        execution_time = time.time() - start_time
        if execution_time > 20:  # Log warning if execution time exceeds 20 seconds
            print(f"Warning: Long execution time: {execution_time:.2f} seconds")
        
        return {
            "message": "Event validated and published successfully",
            "event_id": event_id
        }, 200
        
    except Exception as e:
        return {"error": f"Error publishing event: {str(e)}"}, 500