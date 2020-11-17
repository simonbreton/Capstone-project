CREATE TABLE IF NOT EXISTS
        {{ var.json.env.project }}.{{ var.json.env.production }}.{{ var.json.env.fact }}
        (surrogate_keys STRING,
        partitioned_key TIMESTAMP,
        pickup_datetime TIMESTAMP,
        dropoff_datetime TIMESTAMP,
        passenger_count INT64,
        trip_distance FLOAT64,
        payment_type INT64,
        total_amount FLOAT64)
        PARTITION BY
        TIMESTAMP_TRUNC(partitioned_key, day)