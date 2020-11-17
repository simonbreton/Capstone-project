UPDATE 
	`{{ var.json.env.project }}.{{ var.json.env.stg }}.{{ var.json.env.raw_data }}`
SET 
	surrogate_keys = concat(GENERATE_UUID(),'{{ execution_date }}')
WHERE 
	surrogate_keys = 'null' AND partitioned_key between'{{ execution_date.strftime("%Y-%m-%d") }}' and '{{ next_execution_date.strftime("%Y-%m-%d") }}'