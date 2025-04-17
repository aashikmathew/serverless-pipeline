"""
Frontend application for the serverless data validation pipeline.
Provides a web interface and API endpoints for data validation.
"""
import os
import json
import re
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configuration
PROJECT_ID = os.getenv('PROJECT_ID', 'servless-pipeline')
FUNCTION_URL = os.getenv(
    'VALIDATOR_URL',
    f'https://us-central1-{PROJECT_ID}.cloudfunctions.net/data-validator'
)

def is_valid_email(email):
    """
    Validate email format.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if email is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_data(data):
    """
    Validate data using the Cloud Function.
    
    Args:
        data (dict): The data to validate
        
    Returns:
        tuple: (response_data, status_code)
    """
    try:
        response = requests.post(
            FUNCTION_URL,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        return response.json(), response.status_code
    except requests.exceptions.RequestException as req_error:
        return {'error': str(req_error)}, 500

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/validate', methods=['POST'])
def validate():
    """
    API endpoint to validate data.
    
    Returns:
        tuple: (response_json, status_code)
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['name', 'email', 'age']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Validate email format
        if not is_valid_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400

        # Validate age
        if not isinstance(data.get('age'), int) or data['age'] < 0:
            return jsonify({'error': 'Age must be a positive integer'}), 400

        # Call the validation function
        result, status_code = validate_data(data)
        return jsonify(result), status_code

    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON data'}), 400
    except Exception as error:
        app.logger.error('Error processing request: %s', str(error))
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))) 