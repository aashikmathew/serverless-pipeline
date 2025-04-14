# Pub/Sub Topic for events
resource "google_pubsub_topic" "events" {
  name    = "events-topic"
  labels = {
    env = var.environment
  }
}

# Pub/Sub Subscription
resource "google_pubsub_subscription" "events_subscription" {
  name    = "events-subscription"
  topic   = google_pubsub_topic.events.name
  ack_deadline_seconds = 600

  push_config {
    push_endpoint = google_cloud_run_service.event_processor.status[0].url

    attributes = {
      x-goog-version = "v1"
    }
  }
}

# Cloud Run Service for event processing
resource "google_cloud_run_service" "event_processor" {
  name     = "event-processor"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/cloudrun/hello"  # Using a public hello world image
        
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Cloud Function for data validation
resource "google_cloudfunctions_function" "data_validator" {
  name        = "data-validator"
  description = "Validates incoming data"
  runtime     = var.cloud_function_runtime
  region      = var.region

  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.static_assets.name
  source_archive_object = "functions/data-validator.zip"
  trigger_http          = true
  entry_point           = "validate_data"

  environment_variables = {
    PROJECT_ID = var.project_id
  }
}

# IAM permissions for Cloud Functions
resource "google_cloudfunctions_function_iam_member" "invoker" {
  project        = google_cloudfunctions_function.data_validator.project
  region         = google_cloudfunctions_function.data_validator.region
  cloud_function = google_cloudfunctions_function.data_validator.name

  role   = "roles/cloudfunctions.invoker"
  member = "serviceAccount:${var.service_account_email}"
}

# Cloud Run Service for frontend
resource "google_cloud_run_service" "frontend" {
  name     = var.cloud_run_service_name
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/cloudrun/hello"  # Using a public hello world image
        
        resources {
          limits = {
            cpu    = "1000m"
            memory = "512Mi"
          }
        }

        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# IAM policy for Cloud Run
resource "google_cloud_run_service_iam_member" "public" {
  service  = google_cloud_run_service.frontend.name
  location = google_cloud_run_service.frontend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
} 