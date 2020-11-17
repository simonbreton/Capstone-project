INSERT INTO {{ var.json.env.project }}.{{ var.json.env.production }}.{{ var.json.env.summary }}
SELECT *
FROM `{{ var.json.env.project }}.{{ var.json.env.production }}.{{ var.json.env.fact }}`
LEFT JOIN
`{{ var.json.env.project }}.{{ var.json.env.production }}.{{ var.json.env.geo }}`
USING 
	(surrogate_keys)
WHERE 
	partitioned_key between'{{ execution_date.strftime("%Y-%m-%d") }}' and '{{ next_execution_date.strftime("%Y-%m-%d") }}'