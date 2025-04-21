# Monitoring Dashboard
resource "google_monitoring_dashboard" "pipeline_dashboard" {
  dashboard_json = jsonencode({
    displayName = "Data Processing Pipeline Dashboard"
    gridLayout = {
      columns = 2
      widgets = [
        {
          title = "Frontend Request Count"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "metric.type=\"run.googleapis.com/request_count\" resource.type=\"cloud_run_revision\" resource.label.\"service_name\"=\"${var.cloud_run_service_name}\""
                }
                unitOverride = "1"
              }
            }]
          }
        },
        {
          title = "Function Executions"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "metric.type=\"cloudfunctions.googleapis.com/function/execution_count\" resource.type=\"cloud_function\" resource.label.\"function_name\"=\"data-validator\""
                }
              }
            }]
          }
        },
        {
          title = "Error Rate"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "metric.type=\"run.googleapis.com/request_count\" resource.type=\"cloud_run_revision\" resource.label.\"service_name\"=\"${var.cloud_run_service_name}\" metric.label.\"response_code_class\"=\"4xx\""
                }
              }
            }]
          }
        },
        {
          title = "Pub/Sub Message Count"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "metric.type=\"pubsub.googleapis.com/topic/message_count\" resource.type=\"pubsub_topic\" resource.label.\"topic_id\"=\"events-topic\""
                }
              }
            }]
          }
        }
      ]
    }
  })
}

# Alert Policy for High Error Rate
resource "google_monitoring_alert_policy" "high_error_rate" {
  display_name = "High Error Rate Alert"
  combiner     = "OR"

  conditions {
    display_name = "Error Rate > 5%"
    condition_threshold {
      filter          = "metric.type=\"run.googleapis.com/request_count\" resource.type=\"cloud_run_revision\" resource.label.\"service_name\"=\"${var.cloud_run_service_name}\" metric.label.\"response_code_class\"=\"5xx\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 5.0

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name]
}

# Alert for Function Timeouts
resource "google_monitoring_alert_policy" "function_timeout" {
  display_name = "Function Timeout Alert"
  combiner     = "OR"

  conditions {
    display_name = "Function Timeout Rate"
    condition_threshold {
      filter          = "metric.type=\"cloudfunctions.googleapis.com/function/execution_times\" resource.type=\"cloud_function\" resource.label.\"function_name\"=\"data-validator\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 30000 # 30 seconds

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_PERCENTILE_99"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name]
}

# Email Notification Channel
resource "google_monitoring_notification_channel" "email" {
  display_name = "Email Notification Channel"
  type         = "email"

  labels = {
    email_address = var.alert_email_address
  }
}

# Log Sink to BigQuery
resource "google_logging_project_sink" "pipeline_logs" {
  name        = "pipeline-logs-sink"
  destination = "bigquery.googleapis.com/projects/${var.project_id}/datasets/${google_bigquery_dataset.pipeline_logs.dataset_id}"
  filter      = "resource.type=(\"cloud_run_revision\" OR \"cloud_function\" OR \"pubsub_topic\")"

  unique_writer_identity = true
}

# BigQuery Dataset for Logs
resource "google_bigquery_dataset" "pipeline_logs" {
  dataset_id  = "pipeline_logs"
  description = "Dataset for pipeline logs and analytics"
  location    = "US"

  labels = {
    env = var.environment
  }
}

# BigQuery Table for Processed Data
resource "google_bigquery_table" "processed_data" {
  dataset_id = google_bigquery_dataset.pipeline_logs.dataset_id
  table_id   = "processed_data"

  time_partitioning {
    type = "DAY"
  }

  schema = jsonencode([
    {
      name        = "timestamp"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Event timestamp"
    },
    {
      name        = "event_type"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Type of event"
    },
    {
      name        = "data"
      type        = "JSON"
      mode        = "NULLABLE"
      description = "Event data"
    },
    {
      name        = "status"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Processing status"
    }
  ])
} 