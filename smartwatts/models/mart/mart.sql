with base as (
    select * from {{ ref('hourly_dataset') }}
)

select
    esiid,
    usage_hourly,
    ROUND(usage_kwh, 4)                         as usage_kwh,
    estimated_actual,

    -- time features for ML
    EXTRACT(HOUR from usage_hourly)               as hour_of_day,
    EXTRACT(DAYOFWEEK from usage_hourly)          as day_of_week,
    EXTRACT(MONTH from usage_hourly)              as month,
    EXTRACT(YEAR from usage_hourly)               as year,
    IF(EXTRACT(DAYOFWEEK from usage_hourly)
        IN (1,7), true, false)                  as is_weekend,

    temp_f,
    humidity,
    precipitation,
    snow_inches,
    wind_speed_mph,
    peak_wind_gust_mph,
    pressure_hpa,
    total_sunshine_minutes,
    weather_code

from base