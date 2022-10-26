import os
import logging

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCS_BUCKET")

path_to_local_home = os.environ.get("AIRFLOW_HOME", "opt/airflow")

with DAG(
    dag_id="mapping_teams_id_name",
    schedule_interval="",
    catchup=False,
    start_date= datetime(2022, 10, 26)
) as dag:
    # import functions
    def get_teams_id_mappings():
        from includes.web_scraping import get_current_teams, get_english_teams, generate_csv

        standings_url = os.environ.get('STANDINFS_URL')
        login_url = os.environ.get('LOGIN_URL')
        target_url = os.environ.get('TARGET_URL')
        email = os.environ.get("EMAIL")
        password = os.environ.get("PASSWORD")

        current_clubs = get_current_teams(standings_url)
        id_to_team_mapping = get_english_teams(login_url, target_url, email, password)

        date = {{ ds }}
        execution_year = int(date.split("-")[0])

        file_name = f"{execution_year}_{execution_year + 1}.parquet"

        generate_csv(current_clubs, id_to_team_mapping, file_name)