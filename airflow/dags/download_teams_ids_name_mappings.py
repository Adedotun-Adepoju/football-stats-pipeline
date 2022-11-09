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

execution_date = '{{ execution_date.strftime(\'%Y\') }}'


with DAG(
    dag_id="mapping_teams_id_name",
    schedule_interval="0 8 15 8 *",
    catchup=False,
    start_date= datetime(2022, 10, 26)
) as dag:
    # file_name = f"{execution_year}_{execution_year + 1}_season_teams.parquet"
    file_name = f"{ execution_date }_season_teams.parquet"
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)

    # download files
    def get_teams_id_mappings():
        from includes.web_scraping import get_current_teams, get_english_teams, generate_csv
        
        # logging.info(current_dir)
        logging.info(parent_dir)
        logging.info(os.listdir(parent_dir))

        standings_url = os.environ.get('STANDINGS_URL')
        login_url = os.environ.get('LOGIN_URL')
        target_url = os.environ.get('TARGET_URL')
        email = os.environ.get("EMAIL")
        password = os.environ.get("PASSWORD")

        current_clubs = get_current_teams(standings_url)
        id_to_team_mapping = get_english_teams(login_url, target_url, email, password)

        logging.info(id_to_team_mapping)

        generate_csv(current_clubs, id_to_team_mapping, file_name)

    def upload_gcs(bucket, local_file, object_folder):
        # prevent timeout for files > 6 MB on 800 kbps upload speed
        storage.blob.MAX_MULTIPART_SIZE = 5 * 1024 * 1024 # 5 MB
        storage.blob.DEFAULT_CHUNKSIZE = 5 * 1024 * 1024 # 5 M

        client = storage.Client()
        bucket = client.bucket(bucket)

        gcs_path = f"{object_folder}/{local_file}"

        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(local_file)

    display_version_task = BashOperator(
        task_id="chrome_version",
        bash_command=f'which google-chrome'
    )

    download_dataset_task = PythonOperator(
        task_id="download_teams",
        python_callable=get_teams_id_mappings,
        trigger_rule="all_done"
    )

    upload_gcs_task = PythonOperator(
        task_id="upload_gcs",
        python_callable=upload_gcs,
        op_kwargs= {
            "bucket": BUCKET,
            "local_file": file_name,
            "object_folder": f"seasonal_teams"
        }
    )

    clean_up_task = BashOperator(
        task_id="clean_up_task",
        bash_command=f"rm { file_name }",
        trigger_rule="all_done"
    )

    display_version_task >> download_dataset_task >> upload_gcs_task >> clean_up_task



    