#!/bin/bash

# Set variables
PROJECT_ID="servless-pipeline"
REGION="us-central1"
EMAIL="your-email@example.com"  # Replace with your email

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable monitoring.googleapis.com --project=$PROJECT_ID
gcloud services enable cloudresourcemanager.googleapis.com --project=$PROJECT_ID

# Create notification channel
echo "Creating notification channel..."
gcloud monitoring channels create \
    --display-name="Email Alerts" \
    --type=email \
    --channel-labels=email_address=$EMAIL \
    --project=$PROJECT_ID

# Get the notification channel ID
CHANNEL_ID=$(gcloud monitoring channels list --format="value(name)" --filter="displayName='Email Alerts'" --project=$PROJECT_ID)

# Create alert policy
echo "Creating alert policy..."
gcloud monitoring policies create \
    --policy-from-file=../terraform/alert_policy.json \
    --project=$PROJECT_ID

# Create dashboard
echo "Creating monitoring dashboard..."
gcloud monitoring dashboards create \
    --config-from-file=../terraform/dashboard.json \
    --project=$PROJECT_ID

echo "Monitoring setup complete!" 