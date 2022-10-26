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
    # download files
    def get_teams_id_mappings(ti):
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

        file_name = f"{execution_year}_{execution_year + 1}_season_teams.parquet"
        print(file_name)

        generate_csv(current_clubs, id_to_team_mapping, file_name)

        ti.xcom_push(key='teams_file_name', value=file_name)

    def upload_gcs(bucket, ti, object_folder):
        # prevent timeout for files > 6 MB on 800 kbps upload speed
        storage.blob.MAX_MULTIPART_SIZE = 5 * 1024 * 1024 # 5 MB
        storage.blob.DEFAULT_CHUNKSIZE = 5 * 1024 * 1024 # 5 M

        local_file = ti.xcom_pull(key="teams_file_name", task_ids='download_teams')

        client = storage.Client()
        bucket = client.bucket(bucket)

        gcs_path = f"{object_folder}/{local_file}"

        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(local_file)

    download_dataset_task = PythonOperator(
        task_id="download_teams",
        python_callable=get_teams_id_mappings
    )

    upload_gcs_task = PythonOperator(
        task_id="upload_gcs",
        python_callable=upload_gcs,
        op_kwargs= {
            "bucket": BUCKET,
            "object_folder": f"seasonal_teams"
        }
    )

    