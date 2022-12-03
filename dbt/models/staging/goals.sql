{{ config(materialized='table') }}

SELECT DISTINCT *
FROM {{ source('staging', 'goal_stats_table') }}
WHERE created_at = (SELECT MAX(created_at) FROM {{ source('staging', 'goal_stats_table') }})

