#standardSQL
SELECT 
	COUNT(*),
FROM 
	`{}`
WHERE 
	partitioned_key between'{{ execution_date.strftime("%Y-%m-%d") }}' and '{{ next_execution_date.strftime("%Y-%m-%d") }}'