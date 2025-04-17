variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "service_account_email" {
  description = "Service account email for Cloud Functions and Cloud Run"
  type        = string
}

variable "firestore_location" {
  description = "Location for Firestore database"
  type        = string
  default     = "us-central"
}

variable "bigquery_dataset_name" {
  description = "Name of the BigQuery dataset"
  type        = string
  default     = "analytics"
}

variable "cloud_function_runtime" {
  description = "Runtime for Cloud Functions"
  type        = string
  default     = "python39"
}

variable "cloud_run_service_name" {
  description = "Name of the Cloud Run service"
  type        = string
  default     = "frontend-service"
}

variable "alert_email_address" {
  description = "Email address to receive monitoring alerts"
  type        = string
}

variable "storage_location" {
  description = "Location for storage buckets"
  type        = string
  default     = "US"
}

variable "storage_class" {
  description = "Storage class for buckets"
  type        = string
  default     = "STANDARD"
}

variable "github_owner" {
  description = "GitHub repository owner"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
}

variable "github_branch" {
  description = "GitHub branch to trigger builds from"
  type        = string
  default     = "main"
} 