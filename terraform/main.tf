terraform {
    backend "local" {}
  required_providers {
    google = {
      source = "hashicorp/google"
    #   version = "3.5.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)

  project = var.project
  region  = var.region
}

# data lake 
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
resource "google_storage_bucket" "data-lake-bucket" {
  name          = var.data_lake_bucket 
  location      = var.region

  # Optional, but recommended settings:
  storage_class = var.storage_class
  uniform_bucket_level_access = true

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition { 
      age = 90 // days
    }
  }

   force_destroy = true
}

# Data warehouse
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
resource "google_bigquery_dataset" "football_dataset" {
    dataset_id = var.bq_dataset
    project = var.project
    location = var.region
}

resource "google_bigquery_dataset" "dbt_dataset_dev" {
    dataset_id = var.bq_dbt_dev_dataset
    project = var.project
    location = var.region
}

resource "google_bigquery_dataset" "dbt_dataset_prod" {
    dataset_id = var.bq_dbt_prod_dataset
    project = var.project
    location = var.region
}