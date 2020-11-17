CREATE TABLE IF NOT EXISTS
        {{ var.json.env.project }}.{{ var.json.env.production }}.{{ var.json.env.geo }}
        (surrogate_keys STRING,
        pickup_zone STRING,
        pickup_borough STRING,
        dropoff_zone STRING,
        dropoff_borough STRING)