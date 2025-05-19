# Enable required APIs
# (Removed google_project_service.required_apis resource)

# Create Cloud Run service
resource "google_cloud_run_service" "frontend" {
  name     = var.cloud_run_service_name
  location = var.region
  project  = var.project_id

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/frontend-service:latest"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  # depends_on = [google_project_service.required_apis] (removed)
}

# Create Cloud Function
resource "google_cloudfunctions_function" "data_validator" {
  name        = "data-validator"
  description = "Data validation function"
  runtime     = "python39"
  region      = var.region
  project     = var.project_id

  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.function_bucket.name
  source_archive_object = google_storage_bucket_object.function_zip.name
  trigger_http          = true
  entry_point           = "data_validator"

  # depends_on = [google_project_service.required_apis] (removed)
}

# Create storage bucket for function code
resource "google_storage_bucket" "function_bucket" {
  name                        = "${var.project_id}-function-source"
  location                    = var.storage_location
  project                     = var.project_id
  storage_class               = var.storage_class
  uniform_bucket_level_access = true

  # depends_on = [google_project_service.required_apis] (removed)
}

# Upload function code
resource "google_storage_bucket_object" "function_zip" {
  name   = "function-source.zip"
  bucket = google_storage_bucket.function_bucket.name
  source = "../src/functions/data_validator/function-source.zip" # You'll need to create this zip file
} 