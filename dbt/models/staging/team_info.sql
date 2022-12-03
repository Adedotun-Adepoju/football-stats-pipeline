{{ config(materialized='table') }}

SELECT DISTINCT *
FROM {{ source('staging', 'team_info_table') }} 