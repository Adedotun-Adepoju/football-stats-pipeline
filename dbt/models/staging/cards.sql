{{ config(materialized='table') }}


SELECT DISTINCT *
FROM {{ source('staging', 'cards_stats_table') }} c LEFT JOIN {{ ref('pl_teams_id') }} pl
    ON c.team_id = pl.id 
WHERE created_at = (SELECT MAX(created_at) FROM {{ source('staging', 'cards_stats_table') }})