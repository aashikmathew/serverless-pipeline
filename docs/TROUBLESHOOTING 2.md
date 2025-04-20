# Troubleshooting Guide

## Common Issues and Solutions

### 1. Cloud Function Issues

#### Function Not Triggering
**Symptoms:**
- Pub/Sub messages not being processed
- No logs in Cloud Logging
- Function status shows as inactive

**Solutions:**
1. Check Pub/Sub subscription:
```bash
gcloud pubsub subscriptions describe events-subscription
```

2. Verify function is deployed:
```bash
gcloud functions describe data-validator --region us-central1
```

3. Check IAM permissions:
```bash
gcloud functions get-iam-policy data-validator --region us-central1
```

#### Function Timeout
**Symptoms:**
- Function execution taking too long
- Timeout errors in logs
- Incomplete processing

**Solutions:**
1. Increase timeout duration:
```bash
gcloud functions deploy data-validator --timeout=540s
```

2. Optimize function code:
- Reduce database operations
- Implement batch processing
- Use caching where possible

3. Check resource allocation:
```bash
gcloud functions describe data-validator --region us-central1
```

### 2. Cloud Run Issues

#### Service Not Starting
**Symptoms:**
- 503 Service Unavailable
- Container crash loops
- High latency

**Solutions:**
1. Check container logs:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=frontend-service"
```

2. Verify environment variables:
```bash
gcloud run services describe frontend-service --region us-central1
```

3. Check resource limits:
```bash
gcloud run services describe frontend-service --region us-central1 --format="yaml(spec.template.spec.containers[0].resources)"
```

#### High Latency
**Symptoms:**
- Slow response times
- Timeout errors
- High CPU usage

**Solutions:**
1. Increase concurrency:
```bash
gcloud run deploy frontend-service --concurrency=80
```

2. Enable CPU allocation:
```bash
gcloud run deploy frontend-service --cpu=1
```

3. Implement caching:
- Use Cloud CDN
- Implement in-memory caching
- Use Cloud Storage for static assets

### 3. Pub/Sub Issues

#### Message Backlog
**Symptoms:**
- Growing message count
- High latency
- Processing delays

**Solutions:**
1. Check subscription metrics:
```bash
gcloud pubsub subscriptions describe events-subscription --format="yaml(detailedStatus)"
```

2. Adjust acknowledgment deadline:
```bash
gcloud pubsub subscriptions update events-subscription --ack-deadline=600
```

3. Scale processing capacity:
- Increase function instances
- Implement batch processing
- Optimize processing logic

#### Message Loss
**Symptoms:**
- Missing messages
- Incomplete data
- Processing gaps

**Solutions:**
1. Enable message retention:
```bash
gcloud pubsub topics update events-topic --message-retention-duration=7d
```

2. Implement dead letter queue:
```bash
gcloud pubsub subscriptions create events-subscription-dlq \
  --topic=events-topic-dlq \
  --dead-letter-topic=events-topic
```

3. Add message tracking:
- Implement message IDs
- Add timestamps
- Use Cloud Monitoring

### 4. Firestore Issues

#### High Latency
**Symptoms:**
- Slow queries
- Timeout errors
- High read/write costs

**Solutions:**
1. Optimize queries:
- Add composite indexes
- Use appropriate query operators
- Implement pagination

2. Implement caching:
- Use Cloud Memorystore
- Implement application-level caching
- Use Cloud CDN

3. Monitor usage:
```bash
gcloud firestore indexes composite list
```

#### Quota Exceeded
**Symptoms:**
- 429 Too Many Requests
- Operation denied
- Rate limit errors

**Solutions:**
1. Check quotas:
```bash
gcloud firestore operations list
```

2. Implement rate limiting:
- Add exponential backoff
- Implement request queuing
- Use batch operations

3. Optimize operations:
- Use batch writes
- Implement efficient queries
- Cache frequently accessed data

### 5. Monitoring Issues

#### Missing Metrics
**Symptoms:**
- Gaps in monitoring data
- Incomplete dashboards
- Missing alerts

**Solutions:**
1. Verify metric configuration:
```bash
gcloud monitoring metrics list --filter="resource.type=cloud_function"
```

2. Check alert policies:
```bash
gcloud alpha monitoring policies list
```

3. Verify logging setup:
```bash
gcloud logging sinks list
```

#### False Alerts
**Symptoms:**
- Too many alerts
- Alert fatigue
- Inaccurate notifications

**Solutions:**
1. Adjust alert thresholds:
```bash
gcloud alpha monitoring policies update <policy-id> --policy-from-file=alert-policy.json
```

2. Implement alert aggregation:
- Use alert grouping
- Set up notification channels
- Configure quiet periods

3. Fine-tune alert conditions:
- Adjust duration
- Set up baselines
- Use anomaly detection

## Debugging Tools

### 1. Cloud Logging
```bash
# View function logs
gcloud functions logs read data-validator --region us-central1

# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=frontend-service"

# Export logs to BigQuery
gcloud logging sinks create debug-logs \
  bigquery.googleapis.com/projects/servless-pipeline/datasets/analytics \
  --log-filter="severity>=DEBUG"
```

### 2. Cloud Monitoring
```bash
# View metrics
gcloud monitoring dashboards list

# Check alert policies
gcloud alpha monitoring policies list

# View incidents
gcloud alpha monitoring incidents list
```

### 3. Stackdriver Debugger
```bash
# Set up debugger
gcloud debug targets list

# View snapshots
gcloud debug snapshots list
```

## Support Resources

1. **Documentation**
   - [Cloud Functions Documentation](https://cloud.google.com/functions/docs)
   - [Cloud Run Documentation](https://cloud.google.com/run/docs)
   - [Pub/Sub Documentation](https://cloud.google.com/pubsub/docs)
   - [Firestore Documentation](https://cloud.google.com/firestore/docs)

2. **Community Support**
   - [Google Cloud Community](https://cloud.google.com/community)
   - [Stack Overflow](https://stackoverflow.com/questions/tagged/google-cloud-platform)
   - [GitHub Issues](https://github.com/your-repo/issues)

3. **Professional Support**
   - [Google Cloud Support](https://cloud.google.com/support)
   - [Technical Account Manager](https://cloud.google.com/support/docs/account-management)
   - [Premium Support](https://cloud.google.com/support/premium) 