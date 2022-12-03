{{ config(materialized='view') }}

SELECT DISTINCT *
FROM {{ source('staging', 'team_info_table') }}
WHERE created_at = (SELECT MAX(created_at) FROM {{ source('staging', 'team_info_table') }})