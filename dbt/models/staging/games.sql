{{ config(materialized='view') }}

SELECT DISTINCT *
FROM {{ source('staging', 'game_stats_table') }}
WHERE created_at = (SELECT MAX(created_at) FROM {{ source('staging', 'game_stats_table') }})