import os 
import logging 

from datetime import datetime

from airflow import DAG 
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.contrib.operators import gcs_to_bq

from google.cloud import storage
import time 

with DAG(
    dag_id="statistics",
    schedule_interval="0 6 * * 2",
    catchup=False,
    start_date=datetime(2022, 11, 1)
) as dag:
    team_id_file_path = "gcs://football_stats_datalake/Team_ids/pl_teams.csv"
    path_to_local_home = os.environ.get("AIRFLOW_HOME", "opt/airflow")
    file_suffix = "{{ execution_date.strftime(\'%Y-%m-%d\') }}.csv"
    date =  "{{ execution_date.strftime(\'%Y-%m-%d\') }}"
    goals_stats_template = f'{path_to_local_home}/goals_stats_{file_suffix}'
    cards_stats_template = f'{path_to_local_home}/cards_stats_{file_suffix}'
    games_stats_template = f'{path_to_local_home}/games_stats_{file_suffix}'

    BUCKET = os.environ.get('GCS_BUCKET')
    PROJECT_ID = os.environ.get('PROJECT_ID')
    BIGQUERY_DATASET = os.environ.get('BIGQUERY_DATASET')

    # read team_id 
    def download_stats_files(current_date, goals_file, games_file, cards_file):
        import pandas as pd 
        import requests
        import json 
        df = pd.read_csv(team_id_file_path)

        team_ids = df["team_id"].values 

        host_url = os.environ.get('HOST')
        api_key = os.environ.get('API_KEY')

        # Headers to make requests
        headers = {
            'x-rapidapi-host': host_url,
            'x-rapidapi-key':api_key
        }

        # request url 
        team_stats_url = host_url + "/teams/statistics"

        goals_columns = ["team_id", "season", "created_at", "matches_played", "total_goals", "home_goals", "away_goals", "goal_type", "goals_0_15", "goals_16_30", "goals_31_45", "goals_46_60", "goals_61_75", "goals_76_90"]
        games_columns = ["team_id", "season", "form", "created_at", "matches_played", "home_games", "home_wins", "home_draws", "home_loses", "away_games", "away_wins", "away_draws", "away_loses"]
        cards_columns = ["team_id", "season", "created_at", "matches_played", "card_type", "cards_0_15", "cards_16_30", "cards_31_45", "cards_46_60", "cards_61_75", "cards_76_90"]

        league_id = 39
        logging.info(league_id)

        goals_df = pd.DataFrame(columns = goals_columns)
        games_df = pd.DataFrame(columns = games_columns)
        cards_df = pd.DataFrame(columns = cards_columns)

        count = 0

        for id in team_ids:
            query_params = {
                "team": id,
                "season": 2022,
                "league": league_id
            }

            logging.info(id)
            
            response = requests.get(team_stats_url, headers=headers, params= query_params)
            response = response.json()
            statistics = response.get('response')

            fixtures = statistics.get("fixtures")
            goals = statistics.get("goals")
            cards = statistics.get("cards")

            for goal_type in ['for', 'against']:
                goals_dict = {
                    'team_id': id,
                    "season": 2022,
                    "matches_played": fixtures.get('played').get('total'),
                    'created_at': current_date,
                    "goal_type": goal_type,
                    "total_goals": goals.get(goal_type).get('total').get('total'),
                    "home_goals": goals.get(goal_type).get('total').get('home'),
                    "away_goals": goals.get(goal_type).get('total').get('away'),
                    "goals_0_15": goals.get(goal_type).get('minute').get('0-15').get('total'),
                    "goals_16_30": goals.get(goal_type).get('minute').get('16-30').get('total'),
                    "goals_31_45": goals.get(goal_type).get('minute').get('31-45').get('total'),
                    "goals_46_60": goals.get(goal_type).get('minute').get('46-60').get('total'),
                    "goals_61_75": goals.get(goal_type).get('minute').get('61-75').get('total'),
                    "goals_76_90": goals.get(goal_type).get('minute').get('76-90').get('total'),
                }
                goals_df = goals_df.append(goals_dict, ignore_index=True)
                goals_df["created_at"] = pd.to_datetime(goals_df["created_at"])
            
            for card_type in ['yellow', 'red']:
                cards_dict = {
                    'team_id': id,
                    'season': 2022,
                    "matches_played": fixtures.get('played').get('total'),
                    'created_at': current_date,
                    "card_type": card_type,
                    "cards_0_15": cards.get(card_type).get('0-15').get('total'),
                    "cards_16_30": cards.get(card_type).get('16-30').get('total'),
                    "cards_31_45": cards.get(card_type).get('31-45').get('total'),
                    "cards_46_60": cards.get(card_type).get('46-60').get('total'),
                    "cards_61_75": cards.get(card_type).get('61-75').get('total'),
                    "cards_76_90": cards.get(card_type).get('76-90').get('total'),
                }
                cards_df = cards_df.append(cards_dict, ignore_index=True)
                cards_df["created_at"] = pd.to_datetime(cards_df["created_at"])

            games_dict = {
                'team_id': id,
                'season': 2022,
                'form': statistics.get('form'),
                'created_at': current_date,
                'matches_played': fixtures.get('played').get('total'),
                'home_games': fixtures.get('played').get('home'),
                'home_wins': fixtures.get('wins').get('home'),
                'home_draws':fixtures.get('draws').get('home'),
                'home_loses': fixtures.get('loses').get('home'),
                'away_games': fixtures.get('played').get('away'),
                'away_wins': fixtures.get('wins').get('away'),
                'away_draws': fixtures.get('draws').get('away'),
                'away_loses': fixtures.get('loses').get('away'),
            }

            games_df = games_df.append(games_dict, ignore_index=True)
            games_df["created_at"] = pd.to_datetime(games_df["created_at"])

            if(count == 9):
                logging.info('sleeping')
                time.sleep(70)
                count = 0
            else: 
                count +=1 

        goals_df.to_csv(goals_file, index=False)
        games_df.to_csv(games_file, index=False)
        cards_df.to_csv(cards_file, index=False)

    def upload_to_gcs(bucket, local_file, object_name):
        
        # prevent timeout for files > 6 MB on 800 kbps upload speed
        storage.blob.MAX_MULTIPART_SIZE = 5 * 1024 * 1024 # 5 MB
        storage.blob.DEFAULT_CHUNKSIZE = 5 * 1024 * 1024 # 5 M

        client = storage.Client()
        bucket = client.bucket(bucket)

        blob = bucket.blob(object_name)
        blob.upload_from_filename(local_file)

    
    def upload_stats_to_gcs(bucket, local_file, object_name):
       
        for i, file_name in enumerate(local_file):
            logging.info(object_name[i])     
            upload_to_gcs(bucket, file_name, object_name[i])
            logging.info('Success')


    # define tasks 
    download_stats_tasks = PythonOperator(
        task_id="download_stats_task",
        python_callable= download_stats_files,
        op_kwargs = {
            "current_date": date,
            "goals_file": goals_stats_template,
            "games_file": games_stats_template,
            "cards_file": cards_stats_template
        }
    )

    upload_to_gcs_task = PythonOperator(
        task_id="upload_gcs_task",
        python_callable=upload_stats_to_gcs,
        op_kwargs = {
            "bucket": BUCKET,
            "local_file": [games_stats_template, goals_stats_template, cards_stats_template],
            "object_name": [f'games_stats/{file_suffix}', f'goals_stats/{file_suffix}', f'cards_stats/{file_suffix}']
        }
    )

    load_games_stats_task = gcs_to_bq.GoogleCloudStorageToBigQueryOperator(
        task_id='game_stats_to_bq',
        bucket=BUCKET,
        source_objects = [f'games_stats/{file_suffix}'],
        destination_project_dataset_table=f'football_stats.game_stats_table',
        skip_leading_rows = 1,
        schema_fields = [
            {'name': 'team_id', 'type': 'STRING'},
            {'name': 'season', 'type': 'INTEGER'},
            {'name': 'form', 'type': 'STRING'},
            {'name': 'created_at', 'type': 'DATE'},
            {'name': 'matches_played', 'type': 'INTEGER'},
            {'name': 'home_games', 'type': 'INTEGER'},
            {'name': 'home_wins', 'type': 'INTEGER'},
            {'name': 'home_draws', 'type': 'INTEGER'},
            {'name': 'home_loses', 'type': 'INTEGER'},
            {'name': 'away_games', 'type': 'INTEGER'},
            {'name': 'away_wins', 'type': 'INTEGER'},
            {'name': 'away_draws', 'type': 'INTEGER'},
            {'name': 'away_loses', 'type': 'INTEGER'},
        ],
        write_disposition='WRITE_APPEND'
    )

    load_goals_stats_task = gcs_to_bq.GoogleCloudStorageToBigQueryOperator(
        task_id='goal_stats_to_bq',
        bucket=BUCKET,
        source_objects = [f'goals_stats/{file_suffix}'],
        destination_project_dataset_table=f'football_stats.goal_stats_table',
        skip_leading_rows = 1,
        schema_fields = [
            {'name': 'team_id', 'type': 'STRING'},
            {'name': 'season', 'type': 'INTEGER'},
            {'name': 'created_at', 'type': 'DATE'},
            {'name': 'matches_played', 'type': 'INTEGER'},
            {'name': 'total_goals', 'type': 'INTEGER'},
            {'name': 'home_goals', 'type': 'INTEGER'},
            {'name': 'away_goals', 'type': 'INTEGER'},
            {'name': 'goal_type', 'type': 'STRING'},
            {'name': 'goals_0_15', 'type': 'INTEGER'},
            {'name': 'goals_16_30', 'type': 'INTEGER'},
            {'name': 'goals_31_45', 'type': 'INTEGER'},
            {'name': 'goals_46_60', 'type': 'INTEGER'},
            {'name': 'goals_61_75', 'type': 'INTEGER'},
            {'name': 'goals_76_90', 'type': 'INTEGER'},
        ],
        write_disposition='WRITE_APPEND'
    )

    load_cards_stats_task = gcs_to_bq.GoogleCloudStorageToBigQueryOperator(
        task_id='card_stats_to_bq',
        bucket=BUCKET,
        source_objects = [f'cards_stats/{file_suffix}'],
        destination_project_dataset_table=f'football_stats.cards_stats_table',
        skip_leading_rows = 1,
        schema_fields = [
            {'name': 'team_id', 'type': 'STRING'},
            {'name': 'season', 'type': 'INTEGER'},
            {'name': 'created_at', 'type': 'DATE'},
            {'name': 'matches_played', 'type': 'INTEGER'},
            {'name': 'card_type', 'type': 'STRING'},
            {'name': 'cards_0_15', 'type': 'INTEGER'},
            {'name': 'cards_16_30', 'type': 'INTEGER'},
            {'name': 'cards_31_45', 'type': 'INTEGER'},
            {'name': 'cards_46_60', 'type': 'INTEGER'},
            {'name': 'cards_61_75', 'type': 'INTEGER'},
            {'name': 'cards_76_90', 'type': 'INTEGER'},
        ],
        write_disposition='WRITE_APPEND'
    )

    clean_up_task = BashOperator(
        task_id="clean_up_task",
        bash_command=f"rm { games_stats_template } { goals_stats_template} { cards_stats_template }",
        trigger_rule="all_done"
    )

    download_stats_tasks >> upload_to_gcs_task >> load_games_stats_task >> load_goals_stats_task >> load_cards_stats_task >> clean_up_task