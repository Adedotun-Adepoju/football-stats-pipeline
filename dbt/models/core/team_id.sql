{{ config(materialized='table')}}

SELECT id, team_name
FROM {{ ref('pl_teams_id') }}