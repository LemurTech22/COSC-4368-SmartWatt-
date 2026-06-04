WITH energy AS (
    SELECT * FROM {{ref('stg_energy')}}
),
weather AS (
    SELECT * FROM {{ref('stg_weather')}}
),
hourly_energy AS (
    SELECT 
        esiid,
        TIMESTAMP_TRUNC(usage_start_time, HOUR) AS usage_hourly,
        SUM(usage_kwh)                          AS usage_kwh,
        MIN(estimated_actual)                   AS estimated_actual
    FROM energy
    GROUP BY 1, 2
),
joined_data AS (
    SELECT 
        e.esiid,
        e.usage_hourly,
        e.usage_kwh,
        e.estimated_actual,
        w.temp_f,
        w.dew_point_in_d,
        w.humidity,
        COALESCE(w.precipitation, 0)           AS precipitation,
        COALESCE(w.snow_inches, 0)             AS snow_inches,
        w.wind_speed_mph,
        COALESCE(w.peak_wind_gust_mph,0)       AS peak_wind_gust_mph,
        w.pressure_hPa,
        COALESCE(w.total_sunshine_minutes, 0)  AS total_sunshine_minutes,
        COALESCE(w.weather_code, 0)            AS weather_code
    FROM hourly_energy AS e
    LEFT JOIN weather AS w 
        ON e.usage_hourly = w.weather_timestamp
)
SELECT * FROM joined_data
