INSERT INTO `{{ var.json.env.project }}.{{ var.json.env.stg }}.{{ var.json.env.bad_row }}`
SELECT 
    surrogate_keys,
    partitioned_key,
    {{ task_instance.xcom_pull(task_ids='call_parameters', key='pickup_dimension_name') }} as pickup_datetime, 
    {{ task_instance.xcom_pull(task_ids='call_parameters', key='dropoff_dimension_name') }} as dropoff_datetime, 
    passenger_count, 
    trip_distance, 
    payment_type, 
    total_amount
FROM
    `{{ var.json.env.project }}.{{ var.json.env.stg }}.{{ var.json.env.raw_data }}`
WHERE
    partitioned_key between'{{ execution_date.strftime("%Y-%m-%d") }}' and '{{ next_execution_date.strftime("%Y-%m-%d") }}'
AND     
    pickup_longitude = 0.0
OR 
    pickup_latitude = 0.0
OR
    dropoff_longitude = 0.0
OR
    dropoff_latitude = 0.0