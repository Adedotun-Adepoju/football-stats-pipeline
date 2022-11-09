import os 
import logging 

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage

with DAG(
    dag_id="teams_info",
    schedule_interval="30 00 * * 2",
    catchup=False,
    start_date=datetime(2022, 11, 1)
) as dag:
    team_id_file_path = file_path = "gcs://football_datalake/Team_ids/pl_teams.csv"

    # read team_id
    def read_team_file():
        import pandas as pd
        df = pd.read_csv(file_path)

        print.info(df.shape)

    read_file_task = PythonOperator(
        task_id="read_file",
        python_callable=read_team_file()
    )

    info_task = BashOperator(
        task_id="info_task",
        bash_command="echo 'completed'"
    )

    read_file_task >> info_task