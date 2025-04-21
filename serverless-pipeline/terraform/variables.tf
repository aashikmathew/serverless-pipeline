variable "project_id" {
  description = "The GCP project ID"
  type        = string
  default     = "servless-pipeline"
}

variable "cloud_run_service_name" {
  description = "The name of the Cloud Run service"
  type        = string
  default     = "frontend-service"
}

variable "alert_email_address" {
  description = "Email address to receive monitoring alerts"
  type        = string
  default     = "aashikmathewss@gmail.com"  # You can change this default value
}

variable "environment" {
  description = "Environment name (e.g., dev, prod)"
  type        = string
  default     = "dev"
}

variable "region" {
  description = "The GCP region to deploy resources"
  type        = string
  default     = "us-central1"
}

variable "storage_class" {
  description = "Storage class for GCS buckets"
  type        = string
  default     = "STANDARD"
}

variable "storage_location" {
  description = "Location for storage resources"
  type        = string
  default     = "US"
} 