# Serverless Data Processing Pipeline

This project demonstrates a modern serverless architecture on Google Cloud Platform (GCP) using Terraform for infrastructure as code. The pipeline processes data in real-time and provides analytics capabilities.

## Architecture Overview

The application consists of the following components:

1. **Frontend Layer**
   - Cloud Run service for the web application
   - Cloud Storage for static assets
   - Cloud CDN for content delivery

2. **Data Ingestion Layer**
   - Cloud Pub/Sub for event streaming
   - Cloud Functions for data validation

3. **Processing Layer**
   - Cloud Functions for lightweight processing
   - Cloud Run for complex processing
   - Cloud Dataflow for batch processing

4. **Storage Layer**
   - Firestore for NoSQL data
   - BigQuery for analytics
   - Cloud Storage for raw data

5. **Monitoring and Operations**
   - Cloud Monitoring
   - Cloud Logging
   - Error Reporting

## Prerequisites

- Google Cloud Platform account with billing enabled
- Terraform installed (version >= 1.0.0)
- Google Cloud SDK installed
- Python 3.9+ (for Cloud Functions)

## Setup Instructions

1. Clone this repository
2. Initialize Terraform:
   ```bash
   cd terraform
   terraform init
   ```

3. Create a `terraform.tfvars` file with your configuration:
   ```hcl
   project_id = "your-project-id"
   region     = "us-central1"
   ```

4. Apply the Terraform configuration:
   ```bash
   terraform plan
   terraform apply
   ```

## Project Structure

```
serverless-pipeline/
├── terraform/           # Terraform configuration files
├── src/
│   ├── frontend/       # Frontend application code
│   ├── functions/      # Cloud Functions code
│   └── dataflow/       # Dataflow pipeline code
└── docs/              # Documentation
```

## Features

- Real-time data processing
- Scalable serverless architecture
- Infrastructure as Code
- Monitoring and logging
- Cost optimization
- Security best practices

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. 