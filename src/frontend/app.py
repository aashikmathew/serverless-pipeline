from flask import Flask, render_template, request, jsonify
import os
import requests

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
        data = request.json
        response = requests.post(FUNCTION_URL, json=data)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080))) 