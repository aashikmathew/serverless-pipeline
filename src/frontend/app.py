from flask import Flask, render_template, request, jsonify
import os
import requests
import json

app = Flask(__name__)

# Get environment variables
PROJECT_ID = os.getenv('PROJECT_ID', 'servless-pipeline')
FUNCTION_URL = f'https://us-central1-{PROJECT_ID}.cloudfunctions.net/data-validator'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/validate', methods=['POST'])
def validate_data():
    try:
        # Get the raw JSON data from the request
        data = request.get_json()
        
        # Check if the data is in the expected format
        if 'user' in data:
            # Try to extract fields from nested structure
            user_data = {
                'name': data['user'].get('name', ''),
                'email': data['user'].get('email', ''),
                'age': data['user'].get('age', 0)
            }
            
            # Check if any required fields are missing
            missing_fields = []
            if not user_data['name']:
                missing_fields.append('name')
            if not user_data['email']:
                missing_fields.append('email')
            if not user_data['age']:
                missing_fields.append('age')
                
            if missing_fields:
                return jsonify({
                    'error': f'Missing required fields in user object: {", ".join(missing_fields)}. Please provide all required fields in the correct format.'
                }), 400
        else:
            # Check if all required fields are present in flat structure
            required_fields = ['name', 'email', 'age']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({
                    'error': f'Missing required fields: {", ".join(missing_fields)}. Please provide all required fields in the correct format.'
                }), 400
                
            user_data = data

        # Send the formatted data to the validator function
        response = requests.post(
            FUNCTION_URL,
            json=user_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return jsonify({'message': 'Data validated successfully'}), 200
        else:
            return jsonify({'error': f'Error calling validation service: {response.text}'}), response.status_code
            
    except Exception as e:
        return jsonify({'error': f'Error processing request: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))) 