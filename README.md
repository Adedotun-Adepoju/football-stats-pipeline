# football-stats-pipeline
- [EPL football clubs statistics data pipeline](#football-stats-pipeline)
    - [Problem statement](#problem-statement)
    - [Goal](#main-goal)
    - [Project structure](#structure)

## Problem statement
For passionate football fans like myself, football statistics are very important and I usually find myself digging into it a lot to get more insights about my football club. I find it kind of stressful sometimes looking for answers to some questions about my football club. This is because I don't have a standard website to show me the statistics I need. I find myslef juggling different sites just to get the information I need. I came across a particular website which I find kind of interesting as it contains lots of data about various leagues, clubs, players and seasons and this data can be gotten from different API endpoints. So I decided to work with this data to develop a dashboard showing various statistics for various clubs in England. Examples of data gotten from the API ednpoints:
    - Team information such as founding year, stadium, city
    - Team stats about matches, goals, and bookings
    - Player stats such as goals, injuries e.t.c 

## Main goal
Develop an ETLT data pipeline and dashboard for viewing statistics of clubs in England:
- Call the needed API endpoints
- Create a pipeline for processing the data gotten from the API and converting it to format that can be saved to a data-lake
- Create a pipeline for moving the data from the data lake to a data warehouse
- Transform the data in the warehouse: prepare it for use by the BI tool
- Create a dashboard

## Structure
### Technologies
- Cloud provider: GCP
- Infrastructure as code (IaC): Terraform
- Workflow orchestration: Apache Airflow
- Data Lake: GCS
- Data Warehouse: BigQuery
- Transformations: dbt cloud
- Dashboard: Google Data Studio