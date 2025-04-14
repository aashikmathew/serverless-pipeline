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

# Cloud Run Service
resource "google_cloud_run_service" "frontend" {
  name     = var.cloud_run_service_name
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/${var.cloud_run_service_name}:latest"
        ports {
          container_port = 8080
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

# IAM policy to allow unauthenticated access to Cloud Run service
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.frontend.name
  location = google_cloud_run_service.frontend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Cloud Build trigger for frontend service
resource "google_cloudbuild_trigger" "frontend" {
  name        = "${var.cloud_run_service_name}-trigger"
  description = "Build and deploy frontend service"
  project     = var.project_id

  github {
    owner = var.github_owner
    name  = var.github_repo
    push {
      branch = "^main$"
    }
  }

  included_files = ["src/frontend/**"]

  build {
    step {
      name = "gcr.io/cloud-builders/docker"
      args = ["build", "-t", "gcr.io/${var.project_id}/${var.cloud_run_service_name}:$COMMIT_SHA", "./src/frontend"]
    }

    step {
      name = "gcr.io/cloud-builders/docker"
      args = ["push", "gcr.io/${var.project_id}/${var.cloud_run_service_name}:$COMMIT_SHA"]
    }

    step {
      name = "gcr.io/cloud-builders/gcloud"
      args = ["run", "deploy", var.cloud_run_service_name, "--image", "gcr.io/${var.project_id}/${var.cloud_run_service_name}:$COMMIT_SHA", "--region", var.region, "--platform", "managed", "--allow-unauthenticated"]
    }
  }
} 