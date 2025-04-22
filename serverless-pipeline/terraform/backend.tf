terraform {
  backend "gcs" {
    bucket = "servless-pipeline-tf-state"
    prefix = "terraform/state"
  }
} 