{{ config(materialized='table')}}

SELECT *
FROM {{ ref('pl_teams_id')}}