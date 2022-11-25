import os 
import logging 

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage
import time 

with DAG(
    dag_id="teams_info",
    schedule_interval="0 6 1 * *",
    catchup=False,
    start_date=datetime(2022, 11, 1)
) as dag:
    team_id_file_path = "gcs://football_datalake/Team_ids/pl_teams.csv"
    path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow")
    file_suffix = "{{ execution_date.strftime(\'%Y-%m\') }}.csv"
    team_info_template = f'{path_to_local_home}/team_info_{file_suffix}'

    BUCKET = os.environ.get('GCS_BUCKET')

    # read team_id
    def download_team_info_file(file_name):
        import pandas as pd
        import requests
        import json
        df = pd.read_csv(team_id_file_path)

        team_ids = df["team_id"].values
        logging.info(team_ids)

        host_url = os.environ.get('HOST')
        api_key = os.environ.get('API_KEY')

        # Header to make requests
        headers = {
            'x-rapidapi-host': host_url,
            'x-rapidapi-key':api_key
        }

        # request url
        team_info_url = host_url + '/teams'

        columns = ["team_id", "founded","team_name", "stadium", "capacity", "surface", "city"]
        df = pd.DataFrame(columns = columns)

        count = 0

        for id in team_ids:
            response = requests.get(team_info_url, headers=headers, params={ "id": id })
            response = response.json()
            team_info = response.get('response')
            
            team = team_info[0].get('team')
            venue = team_info[0].get('venue')

            founded = team.get("founded")
            team_name = team.get("name")
            stadium =  venue.get("name")
            capacity = venue.get("capacity")
            surface = venue.get("surface")
            city = venue.get("city")

            team_dict = {
                'team_id': id,
                'founded': founded,
                'team_name': team_name,
                'stadium': stadium,
                'capacity': capacity,
                'surface': surface,
                'city': city
            }

            df = df.append(team_dict, ignore_index=True)
            
            if(count == 10):
                time.sleep(70)
                count = 0
            else:
                count += 1 

        df.to_csv(file_name, index=False)

    def upload_to_gcs(bucket, local_file, object_name):
        
        current_dir = os.getcwd()
        parent_dir = os.path.dirname(current_dir)
        
        # prevent timeout for files > 6 MB on 800 kbps upload speed
        storage.blob.MAX_MULTIPART_SIZE = 5 * 1024 * 1024 # 5 MB
        storage.blob.DEFAULT_CHUNKSIZE = 5 * 1024 * 1024 # 5 M

        client = storage.Client()
        bucket = client.bucket(bucket)

        blob = bucket.blob(object_name)
        blob.upload_from_filename(local_file)


    download_team_info_task = PythonOperator(
        task_id="download_team_info_task",
        python_callable=download_team_info_file,
        op_kwargs = {
            "file_name": team_info_template
        }
    )

    upload_to_gcs_task = PythonOperator(
        task_id="upload_gcs_task",
        python_callable=upload_to_gcs,
        op_kwargs = {
            "bucket": BUCKET,
            "local_file":team_info_template,
            "object_name": f'team_info/{file_suffix}'
        }
    )

    clean_up_task = BashOperator(
        task_id="clean_up_task",
        bash_command=f"rm { team_info_template }",
        trigger_rule="all_done"
    )

    download_team_info_task >> upload_to_gcs_task >> clean_up_task