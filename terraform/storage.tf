# Static assets bucket
resource "google_storage_bucket" "static_assets" {
  name          = "${var.project_id}-static-assets"
  location      = var.storage_location
  storage_class = var.storage_class
  force_destroy = true

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30  # days
    }
    action {
      type = "Delete"
    }
  }
}

# Function source code bucket
resource "google_storage_bucket" "function_source" {
  name          = "${var.project_id}-function-source"
  location      = var.storage_location
  storage_class = var.storage_class
  force_destroy = true

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30  # days
    }
    action {
      type = "Delete"
    }
  }
}

# IAM binding for function source bucket
resource "google_storage_bucket_iam_member" "function_source_viewer" {
  bucket = google_storage_bucket.function_source.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${var.service_account_email}"
}

# IAM binding for static assets bucket
resource "google_storage_bucket_iam_member" "static_assets_viewer" {
  bucket = google_storage_bucket.static_assets.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${var.service_account_email}"
}

# Cloud Function source code
resource "google_storage_bucket_object" "function_source" {
  name   = "functions/data-validator.zip"
  bucket = google_storage_bucket.function_source.name
  source = "../src/functions/data_validator/data-validator.zip"

  depends_on = [
    google_storage_bucket.function_source
  ]
}

# Firestore Database
resource "google_firestore_database" "database" {
  name        = "(default)"
  location_id = "nam5"  # Changed from us-central to nam5 (US Central)
  type        = "FIRESTORE_NATIVE"
}

# BigQuery Dataset
resource "google_bigquery_dataset" "analytics" {
  dataset_id    = var.bigquery_dataset_name
  friendly_name = "Analytics Dataset"
  description   = "Dataset for storing analytics data"
  location      = var.region

  labels = {
    env = var.environment
  }
}

# BigQuery Table for analytics
resource "google_bigquery_table" "events" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "events"

  schema = <<EOF
[
  {
    "name": "event_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "timestamp",
    "type": "TIMESTAMP",
    "mode": "REQUIRED"
  },
  {
    "name": "event_type",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "data",
    "type": "STRING",
    "mode": "NULLABLE"
  }
]
EOF

  time_partitioning {
    type  = "DAY"
    field = "timestamp"
  }
}

# Firestore backup bucket
resource "google_storage_bucket" "firestore_backup" {
  name          = "${var.project_id}-firestore-backup"
  location      = var.storage_location
  storage_class = var.storage_class
  force_destroy = false  # Prevent accidental deletion of backups

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90  # Keep backups for 90 days
    }
    action {
      type = "Delete"
    }
  }

  retention_policy {
    is_locked        = true
    retention_period = 2592000  # 30 days minimum retention
  }
}

# IAM binding for Firestore backup service account
resource "google_storage_bucket_iam_member" "firestore_backup_writer" {
  bucket = google_storage_bucket.firestore_backup.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.service_account_email}"
}

# Scheduled Firestore backup
resource "google_cloud_scheduler_job" "firestore_backup" {
  name        = "firestore-scheduled-backup"
  description = "Triggers daily Firestore backup"
  schedule    = "0 0 * * *"  # Run daily at midnight
  time_zone   = "UTC"

  http_target {
    http_method = "POST"
    uri         = "https://firestore.googleapis.com/v1/projects/${var.project_id}/databases/(default):exportDocuments"
    
    oauth_token {
      service_account_email = var.service_account_email
    }

    body = base64encode(jsonencode({
      outputUriPrefix: "gs://${google_storage_bucket.firestore_backup.name}/backups/${formatdate("YYYY-MM-DD", timestamp())}"
    }))
  }
}

# Grant Firestore export permission to service account
resource "google_project_iam_member" "firestore_export" {
  project = var.project_id
  role    = "roles/datastore.importExportAdmin"
  member  = "serviceAccount:${var.service_account_email}"
}

# Cloud Function to verify backup completion
resource "google_storage_bucket_object" "backup_verifier_source" {
  name   = "functions/backup-verifier.zip"
  bucket = google_storage_bucket.function_source.name
  source = "../src/functions/backup_verifier/backup-verifier.zip"

  depends_on = [
    google_storage_bucket.function_source
  ]
}

resource "google_cloudfunctions_function" "backup_verifier" {
  name        = "backup-verifier"
  description = "Verifies Firestore backup completion and sends notification"
  runtime     = var.cloud_function_runtime
  region      = var.region

  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.function_source.name
  source_archive_object = google_storage_bucket_object.backup_verifier_source.name
  
  event_trigger {
    event_type = "google.storage.object.finalize"
    resource   = google_storage_bucket.firestore_backup.name
  }

  environment_variables = {
    PROJECT_ID = var.project_id
    TOPIC_NAME = google_pubsub_topic.backup_notifications.name
  }
}

# Pub/Sub topic for backup notifications
resource "google_pubsub_topic" "backup_notifications" {
  name = "firestore-backup-notifications"
  labels = {
    env = var.environment
  }
} 