# Serverless Data Processing Pipeline on GCP

A modern serverless architecture built on Google Cloud Platform (GCP) using Terraform for Infrastructure as Code (IaC). The pipeline processes data in real-time and provides analytics capabilities.

## 🚀 Features

- **Real-time Data Processing**
  - Cloud Run for serverless container execution
  - Cloud Functions for event processing
  - Pub/Sub for event streaming
  - Firestore for NoSQL data storage
  - BigQuery for analytics
  - Cloud Storage for static assets

- **Error Handling & Reliability**
  - Dead Letter Queue (DLQ) for failed messages
  - Retry mechanism with exponential backoff
  - Error tracking and monitoring
  - Automatic error recovery

- **Monitoring & Observability**
  - Cloud Monitoring dashboards
  - Log exports to BigQuery
  - Alerting policies for error rates
  - Performance metrics tracking

## 🛠️ Tech Stack

- **Infrastructure**
  - Terraform for IaC
  - Google Cloud Platform
  - Cloud Run
  - Cloud Functions
  - Pub/Sub
  - Firestore
  - BigQuery
  - Cloud Storage

- **Development**
  - Python 3.9
  - Cloud Functions Framework
  - Pub/Sub Client Library
  - Flask

## 📋 Project Structure

```
serverless-pipeline/
├── src/
│   └── functions/
│       └── data_validator/
│           ├── main.py           # Cloud Function code
│           └── requirements.txt  # Dependencies
├── terraform/                    # Infrastructure code
└── README.md
```

## 🔧 Setup & Deployment

1. **Prerequisites**
   - Google Cloud Project
   - Terraform installed
   - gcloud CLI configured

2. **Infrastructure Setup**
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

3. **Function Deployment**
   ```bash
   ./deploy_function.sh
   ```

4. **Testing**
   ```bash
   # Test with valid payload
   curl -X POST "https://us-central1-servless-pipeline.cloudfunctions.net/data-validator" \
     -H "Content-Type: application/json" \
     -d '{"event_type": "test", "data": "test data"}'

   # Test with invalid payload
   curl -X POST "https://us-central1-servless-pipeline.cloudfunctions.net/data-validator" \
     -H "Content-Type: application/json" \
     -d '{"event_type": "test"}'
   ```

## 🔍 Monitoring

- **Dashboards**
  - Function invocations
  - Execution times
  - Error rates
  - Pub/Sub message counts

- **Logs**
  - Export to BigQuery
  - Error tracking
  - Performance metrics

- **Alerts**
  - High error rates
  - Failed messages
  - Performance issues

## 🔒 Error Handling

- **Dead Letter Queue**
  - Failed messages are sent to DLQ
  - Retry count tracking
  - Error details included

- **Retry Mechanism**
  - Up to 3 retry attempts
  - Exponential backoff
  - Automatic recovery

## 📈 Next Steps

1. **Additional Features**
   - Data transformation
   - Authentication
   - Rate limiting
   - Caching

2. **CI/CD Pipeline**
   - Automated testing
   - Deployment automation
   - Version control

3. **Documentation**
   - API documentation
   - Deployment guides
   - Troubleshooting guides

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is licensed under the MIT License. 