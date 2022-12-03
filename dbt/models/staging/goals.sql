{{ config(materialized='table') }}

SELECT DISTINCT *
FROM {{ source('staging', 'goal_stats_table') }} g LEFT JOIN {{ ref('pl_teams_id')}} pl
    ON g.team_id = pl.id 
WHERE created_at = (SELECT MAX(created_at) FROM {{ source('staging', 'goal_stats_table') }})

