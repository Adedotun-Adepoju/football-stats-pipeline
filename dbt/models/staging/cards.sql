{{ config(materialized='table') }}

SELECT DISTINCT *
FROM {{ source('staging', 'cards_stats_table') }}
WHERE created_at = (SELECT MAX(created_at) FROM {{ source('staging', 'cards_stats_table') }})