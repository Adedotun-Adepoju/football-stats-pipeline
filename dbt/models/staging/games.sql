{{ config(materialized='table') }}

WITH games AS (
    SELECT *
    FROM {{ source('staging', 'game_stats_table') }}
    WHERE created_at = (SELECT MAX(created_at) FROM {{ source('staging', 'game_stats_table') }})
), 

team AS (
    SELECT *
    FROM {{ ref('pl_teams_id')}}
),

final AS (
    SELECT * 
    FROM games LEFT JOIN team 
        ON team.id = games.team_id
)

SELECT * FROM final