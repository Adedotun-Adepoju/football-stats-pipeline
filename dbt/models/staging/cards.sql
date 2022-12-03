{{ config(materialized='table') }}

WITH cards AS (
    SELECT *
    FROM {{ source('staging', 'cards_stats_table') }}
    WHERE created_at = (SELECT MAX(created_at) FROM {{ source('staging', 'cards_stats_table') }})
), 

team AS (
    SELECT *
    FROM {{ ref('pl_teams_id') }}
),

final AS (
    SELECT * 
    FROM cards LEFT JOIN team 
        ON team.id = cards.team_id
)

SELECT * FROM final