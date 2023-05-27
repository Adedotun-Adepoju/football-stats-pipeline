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
resource "google_storage_bucket" "football_stats_data_lake" {
  name          = var.football_data_lake_bucket 
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
    dataset_id = var.football_bq_dataset
    project = var.project
    location = var.region
}

resource "google_bigquery_dataset" "football_dbt_dev" {
    dataset_id = var.football_bq_dbt_dev
    project = var.project
    location = var.region
}

resource "google_bigquery_dataset" "football_dbt_prod" {
    dataset_id = var.football_bq_dbt_prod
    project = var.project
    location = var.region
}

# Compute engine
# Ref: https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_instance
resource "google_compute_instance" "default" {
  name = var.compute_engine
  region = var.region
  zone = var.zone
  machine_type = "custom-4-16384" # 4 CPUs and 16GB ram

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
      type = "pd-balanced"
      size = 30
    }
  }

  network_interface {
    network = "default"

    access_config {
      // Ephemeral public IP
    }
  }
}