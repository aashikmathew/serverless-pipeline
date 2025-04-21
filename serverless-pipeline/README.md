# 🚀 Serverless Data Processing Pipeline on GCP

A modern, event-driven serverless architecture built on Google Cloud Platform (GCP) that processes and validates data in real-time. The pipeline uses Cloud Functions for data validation, Pub/Sub for message streaming, and provides a clean web interface for data submission.

## 📊 Architecture Overview

```ascii
┌──────────────┐     ┌───────────────┐     ┌───────────────┐
│   Frontend   │────▶│ Data Validator│────▶│   Pub/Sub     │
│  (Cloud Run) │     │(Cloud Function)│     │(events-topic) │
└──────────────┘     └───────────────┘     └───────────┬───┘
                            │                           │
                            │                           ▼
┌──────────────┐     ┌─────┴───────┐           ┌──────────────┐
│  Monitoring  │◀────│   Logging   │           │  Subscriber  │
│  Dashboard   │     │    Sink     │           │  Services    │
└──────────────┘     └───────────┬─┘           └──────────────┘
                                 │
                                ▼
                         ┌──────────────┐
                         │   BigQuery   │
                         │  Analytics   │
                         └──────────────┘
```

## 🎯 Key Features

### 1. Frontend Service (Cloud Run)
- Modern web interface for data submission
- Built with Flask and Bootstrap
- Containerized with Docker
- Automatic scaling based on load
- HTTPS endpoint with custom domain support

### 2. Data Validation (Cloud Function)
- Real-time data validation
- JSON schema validation
- Email format verification
- Age validation
- Comprehensive error handling
- Returns detailed validation feedback

### 3. Event Streaming (Pub/Sub)
- Asynchronous message processing
- Guaranteed message delivery
- Dead Letter Queue (DLQ) for failed messages
- Topic/Subscription based architecture
- Real-time event propagation

### 4. Monitoring & Analytics
- Real-time monitoring dashboard
- Function execution metrics
- Message flow visualization
- Error rate tracking
- Performance analytics
- Log-based metrics

## 🛠️ Tech Stack

### Infrastructure
- **Google Cloud Platform**
  - Cloud Run (Frontend hosting)
  - Cloud Functions (Serverless compute)
  - Cloud Pub/Sub (Event streaming)
  - Cloud Monitoring (Observability)
  - Cloud Logging (Audit & debugging)
  - BigQuery (Analytics)

### Development
- **Frontend**
  - Python 3.9
  - Flask web framework
  - Bootstrap 5
  - Gunicorn server
  - Docker

- **Backend**
  - Python Cloud Functions
  - functions-framework
  - google-cloud-pubsub
  - JSON schema validation

### DevOps
- Terraform (Infrastructure as Code)
- GitHub (Version Control)
- Cloud Build (CI/CD)

## 📁 Project Structure

```
serverless-pipeline/
├── src/
│   ├── frontend/
│   │   ├── Dockerfile           # Container configuration
│   │   ├── app.py              # Flask application
│   │   ├── requirements.txt    # Python dependencies
│   │   └── templates/
│   │       └── index.html      # Web interface
│   │
│   └── functions/
│       └── data_validator/
│           ├── main.py         # Validation logic
│           └── requirements.txt # Function dependencies
│
├── terraform/
│   ├── main.tf                 # Main infrastructure
│   ├── variables.tf            # Variable definitions
│   └── serverless.tf          # Serverless resources
│
└── README.md
```

## 🔧 Setup & Deployment

### Prerequisites
1. **Google Cloud Setup**
   ```bash
   # Install Google Cloud SDK
   brew install google-cloud-sdk  # macOS
   
   # Initialize and set project
   gcloud init
   gcloud config set project servless-pipeline
   ```

2. **Terraform Setup**
   ```bash
   # Install Terraform
   brew install terraform  # macOS
   
   # Initialize Terraform
   cd terraform
   terraform init
   ```

### Deployment Steps

1. **Infrastructure Deployment**
   ```bash
   # Deploy GCP resources
   cd terraform
   terraform plan    # Review changes
   terraform apply   # Deploy infrastructure
   ```

2. **Frontend Deployment**
   ```bash
   # Build and deploy frontend
   cd src/frontend
   docker build -t gcr.io/servless-pipeline/frontend-service:latest .
   docker push gcr.io/servless-pipeline/frontend-service:latest
   gcloud run deploy frontend-service --image gcr.io/servless-pipeline/frontend-service:latest
   ```

3. **Function Deployment**
   ```bash
   # Deploy validator function
   cd src/functions/data_validator
   gcloud functions deploy data-validator \
     --runtime python39 \
     --trigger-http \
     --allow-unauthenticated
   ```

## 🧪 Testing

### Frontend Testing
```bash
# Access the frontend URL
open $(gcloud run services describe frontend-service --format='value(status.url)')
```

### Function Testing
```bash
# Test with valid data
curl -X POST "$(gcloud functions describe data-validator --format='value(httpsTrigger.url)')" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "age": 30}'

# Test with invalid data
curl -X POST "$(gcloud functions describe data-validator --format='value(httpsTrigger.url)')" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "invalid-email", "age": -1}'
```

## 📊 Monitoring

### Dashboard Access
1. Open GCP Console
2. Navigate to Monitoring → Dashboards
3. Select "Data Processing Pipeline"

### Key Metrics
- Function Execution Count
- Average Response Time
- Error Rate
- Message Publication Rate
- Message Processing Rate

### Alerts
- High Error Rate Alert (>5%)
- Function Timeout Alert
- Message Processing Delay Alert

## 🔍 Troubleshooting

### Common Issues
1. **Function Returns 500**
   - Check function logs
   - Verify PROJECT_ID environment variable
   - Validate input data format

2. **Message Publishing Fails**
   - Check Pub/Sub permissions
   - Verify topic existence
   - Check quota limits

3. **Frontend Unavailable**
   - Check Cloud Run logs
   - Verify container health
   - Check resource allocation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 📞 Support

For support, please:
1. Check the documentation
2. Review troubleshooting guide
3. Open an issue on GitHub
4. Contact the maintainers

## CI/CD Pipeline

The project includes a comprehensive CI/CD pipeline using GitHub Actions that automates:

1. **Testing**
   - Runs Python unit tests
   - Validates code quality
   - Ensures all components are working correctly

2. **Building**
   - Builds Docker images for the frontend service
   - Packages Cloud Functions
   - Validates Terraform configurations

3. **Deployment**
   - Automatically deploys to GCP on merge to main
   - Updates Cloud Run services
   - Deploys Cloud Functions
   - Applies Terraform changes

### Pipeline Steps
1. Code Push/PR to main branch triggers the pipeline
2. Runs tests and validation
3. Builds Docker images and pushes to GCR
4. Deploys frontend to Cloud Run
5. Updates Cloud Functions
6. Applies Terraform changes

### Required Secrets
To use the CI/CD pipeline, set up the following GitHub secrets:
- `GCP_SA_KEY`: Service account key with necessary permissions
- `PROJECT_ID`: Your GCP project ID

## Latest Deployment
Last tested: 2024-03-19 