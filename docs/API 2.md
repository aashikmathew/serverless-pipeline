# API Documentation

## Overview
This document provides detailed information about the API endpoints available in the Serverless Pipeline application.

## Base URL
The base URL for all API endpoints is: `https://frontend-service-<project-id>-<region>.a.run.app`

## Endpoints

### 1. Data Validation
Validates incoming JSON data against predefined schema.

**Endpoint:** `/api/validate`

**Method:** `POST`

**Request Body:**
```json
{
  "name": "string",
  "email": "string",
  "age": number,
  "address": {
    "street": "string",
    "city": "string",
    "state": "string",
    "zip": "string"
  }
}
```

**Response:**
- Success (200):
```json
{
  "status": "success",
  "message": "Data validated successfully",
  "data": {
    // Original data
  }
}
```
- Error (400):
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": [
    {
      "field": "string",
      "message": "string"
    }
  ]
}
```

### 2. Health Check
Checks the health status of the service.

**Endpoint:** `/health`

**Method:** `GET`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "ISO-8601 timestamp"
}
```

## Error Codes
- 200: Success
- 400: Bad Request - Invalid input data
- 500: Internal Server Error - Server-side error

## Rate Limiting
- 100 requests per minute per IP address
- Rate limit headers included in responses:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Time until limit resets

## Authentication
Currently, the API is publicly accessible. Future versions will implement authentication using:
- API Keys
- OAuth 2.0
- JWT Tokens

## Data Validation Rules
1. Name:
   - Required
   - Minimum length: 2 characters
   - Maximum length: 100 characters

2. Email:
   - Required
   - Must be valid email format
   - Maximum length: 255 characters

3. Age:
   - Required
   - Must be positive integer
   - Must be between 0 and 120

4. Address:
   - Required
   - All fields must be non-empty strings
   - ZIP code must be valid format

## Example Usage

### cURL
```bash
curl -X POST https://frontend-service-<project-id>-<region>.a.run.app/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30,
    "address": {
      "street": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "zip": "12345"
    }
  }'
```

### Python
```python
import requests

url = "https://frontend-service-<project-id>-<region>.a.run.app/api/validate"
data = {
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30,
    "address": {
        "street": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "zip": "12345"
    }
}

response = requests.post(url, json=data)
print(response.json())
```

## Versioning
The API is currently at version 1.0. Future versions will be indicated in the URL path:
- Current: `/api/validate`
- Future: `/api/v2/validate`

## Support
For API support or to report issues:
- Email: support@example.com
- GitHub Issues: https://github.com/your-repo/issues 