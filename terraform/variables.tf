variable project {
    description = "Your GCP Project ID"
}

variable "credentials" {
    description = "path to service account key"
    default = "~/.google/credentials/football-stats-366417-05df9d28434b.json"
}

variable "region" {
    description = "Region for GCP resources"
    default = "europe-west1"
    type = string
}

variable "data_lake_bucket" {
    description = "The name of the GCS bucket to store raw files"
    default = "football_datalake"
}

variable "storage_class" {
    description = "Storage class type for your bucket"
    default = "STANDARD"
}

variable "bq_dataset" {
    description = "BIGQUERY Datatset to write data to"
    type = string
    default = "football_stats"
}

variable "bq_dbt_dev_dataset" {
    description = "BigQuery dataset to be used by dbt during developement"
    type = string
    default = "dbt_development"
}

variable "bq_dbt_prod_dataset" {
    description = "BigQuery Dataset to be used by dbt during production"
    type = string
    default = "production"
}