# Cloud Storage Bucket for static assets
resource "google_storage_bucket" "static_assets" {
  name          = "${var.project_id}-static-assets"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
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