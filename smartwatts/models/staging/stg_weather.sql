WITH source as (
    SELECT * FROM {{source('smartwatts', 'raw_weather')}}
),

cleaned AS (
    SELECT
        CAST(timestamp AS TIMESTAMP) AS weather_timestamp,
        CAST(temp as FLOAT64)        AS temp_c,
        CAST(dwpt as FLOAT64)        AS dew_point_in_d,
        CAST(rhum as INT64)            AS humidity,
        CAST(prcp as FLOAT64)        AS precipitation,
        CAST(snow as INT64)            AS snow_mm,
        CAST(wdir as INT64)            AS wind_direction_degrees,
        CAST(wspd as FLOAT64)        AS wind_speed_kmh,
        CAST(wpgt as FLOAT64)        AS peak_wind_gust_kmh,
        CAST(pres as FLOAT64)        AS pressure_hPa,
        CAST(tsun as INT64)            AS total_sunshine_minutes,
        CAST(coco as INT64)            AS weather_code,


        ROUND((CAST(temp AS FLOAT64)* 9/5)+32, 2)      AS temp_f,
        ROUND(CAST(snow AS INT64)/25.4,0)              AS snow_inches,
        ROUND(CAST(wspd AS FLOAT64) / 1.609, 1)        AS wind_speed_mph,
        ROUND(CAST(wpgt AS FLOAT64) / 1.609, 1)        AS peak_wind_gust_mph,
    
    FROM source
)

SELECT * FROM cleaned