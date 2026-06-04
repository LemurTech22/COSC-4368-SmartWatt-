with source as (
    SELECT * FROM {{source('smartwatts','raw_meter_usage')}}
),

cleaned as (
    SELECT 
        ESIID                              AS esiid,
        PARSE_DATE('%m/%d/%Y', USAGE_DATE) AS usage_date,
        PARSE_TIMESTAMP(
            '%m/%d/%Y %H:%M',
            CONCAT(USAGE_DATE,' ', USAGE_START_TIME)
        )                                  AS usage_start_time,
        PARSE_TIMESTAMP(
            '%m/%d/%Y %H:%M',
            CONCAT(USAGE_DATE, ' ', USAGE_END_TIME
            ) 
        )                                  AS usage_end_time,

        CAST(USAGE_KWH AS FLOAT64)         AS usage_kwh,
        ESTIMATED_ACTUAL                   AS estimated_actual,
    FROM source
)

SELECT * FROM cleaned