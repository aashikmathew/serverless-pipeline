# Deployment Guide

## Prerequisites
- Google Cloud Platform account
- Google Cloud SDK installed
- Terraform installed
- Docker installed
- Python 3.9 or later
- Git installed

## Initial Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/serverless-pipeline.git
cd serverless-pipeline
```

### 2. Configure Google Cloud
```bash
# Login to Google Cloud
gcloud auth login

# Set the project
gcloud config set project servless-pipeline

# Enable required APIs
gcloud services enable \
  cloudfunctions.googleapis.com \
  run.googleapis.com \
  pubsub.googleapis.com \
  firestore.googleapis.com \
  bigquery.googleapis.com \
  storage.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com
```

### 3. Configure Terraform
```bash
cd terraform

# Initialize Terraform
terraform init

# Review the plan
terraform plan

# Apply the configuration
terraform apply
```

## Deploying Components

### 1. Deploy Cloud Function
```bash
cd src/functions/data_validator

# Deploy the function
gcloud functions deploy data-validator \
  --runtime python39 \
  --trigger-topic events-topic \
  --entry-point data_validator \
  --region us-central1 \
  --project servless-pipeline
```

### 2. Deploy Frontend Service
```bash
cd src/frontend

# Build the Docker image
docker build --platform linux/amd64 -t gcr.io/servless-pipeline/frontend-service:latest .

# Push the image to Google Container Registry
docker push gcr.io/servless-pipeline/frontend-service:latest

# Deploy to Cloud Run
gcloud run deploy frontend-service \
  --image gcr.io/servless-pipeline/frontend-service:latest \
  --platform managed \
  --region us-central1 \
  --project servless-pipeline
```

## Environment Configuration

### 1. Set Environment Variables
```bash
# For Cloud Function
gcloud functions deploy data-validator \
  --set-env-vars PROJECT_ID=servless-pipeline

# For Cloud Run
gcloud run deploy frontend-service \
  --set-env-vars PROJECT_ID=servless-pipeline
```

### 2. Configure IAM Roles
```bash
# Grant Pub/Sub Publisher role to Cloud Run service
gcloud projects add-iam-policy-binding servless-pipeline \
  --member="serviceAccount:serverless-sa@servless-pipeline.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher"

# Grant Firestore access
gcloud projects add-iam-policy-binding servless-pipeline \
  --member="serviceAccount:serverless-sa@servless-pipeline.iam.gserviceaccount.com" \
  --role="roles/datastore.user"
```

## Monitoring Setup

### 1. Configure Logging
```bash
# Create log sink
gcloud logging sinks create serverless-logs \
  bigquery.googleapis.com/projects/servless-pipeline/datasets/analytics \
  --log-filter="resource.type=cloud_function OR resource.type=cloud_run_revision"
```

### 2. Set Up Alerts
```bash
# Create alert policy
gcloud alpha monitoring policies create \
  --policy-from-file=alert-policy.json
```

## Verification Steps

### 1. Check Deployment Status
```bash
# Check Cloud Function
gcloud functions describe data-validator --region us-central1

# Check Cloud Run
gcloud run services describe frontend-service --region us-central1
```

### 2. Test the Application
```bash
# Get the Cloud Run URL
FRONTEND_URL=$(gcloud run services describe frontend-service --region us-central1 --format='value(status.url)')

# Test the API
curl -X POST $FRONTEND_URL/api/validate \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com","age":30}'
```

## Troubleshooting

### Common Issues

1. **Permission Errors**
   - Verify IAM roles are correctly assigned
   - Check service account permissions
   - Ensure API is enabled

2. **Deployment Failures**
   - Check Cloud Build logs
   - Verify Docker image builds successfully
   - Ensure environment variables are set

3. **Function Timeouts**
   - Increase timeout duration
   - Optimize function code
   - Check resource allocation

4. **Connectivity Issues**
   - Verify network configuration
   - Check firewall rules
   - Test service endpoints

## Maintenance

### Regular Tasks
1. Monitor resource usage
2. Review logs for errors
3. Update dependencies
4. Backup data regularly

### Scaling
- Cloud Run automatically scales
- Pub/Sub handles message queuing
- Firestore scales automatically
- BigQuery is serverless

## Rollback Procedures

### 1. Cloud Function Rollback
```bash
gcloud functions deploy data-validator \
  --version-id <previous-version>
```

### 2. Cloud Run Rollback
```bash
gcloud run deploy frontend-service \
  --image gcr.io/servless-pipeline/frontend-service:<previous-tag>
```

## Cleanup
To remove all resources:
```bash
cd terraform
terraform destroy
``` 