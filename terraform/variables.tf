variable project {
    description = "Your GCP Project ID"
}

variable "credentials" {
    description = "path to service account key"
    default = "~/.google/credentials/data-engineering-388013-76effb46e8dc.json"
}

variable "region" {
    description = "Region for GCP resources"
    default = "europe-west1"
    type = string
}

variable "zone"{
    description = "Zone for GCP resources"
    default = "europe-west1-b"
}

variable "football_data_lake_bucket" {
    description = "The name of the GCS bucket to store raw files"
    default = "football_stats_datalake"
}

variable "storage_class" {
    description = "Storage class type for your bucket"
    default = "STANDARD"
}

variable "football_bq_dataset" {
    description = "BIGQUERY Datatset to write data to"
    type = string
    default = "football_stats"
}

variable "football_bq_dbt_dev" {
    description = "BigQuery dataset to be used by dbt during developement"
    type = string
    default = "football_dbt_development"
}

variable "football_bq_dbt_prod" {
    description = "BigQuery Dataset to be used by dbt during production"
    type = string
    default = "football_dbt_production"
}

variable "compute_engine" {
    description = "VM instance name"
    type=string
    default = "data-pipeline-engine"
}