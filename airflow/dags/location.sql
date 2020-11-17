INSERT INTO `{}`
WITH
	data_point AS (
  		SELECT
    		surrogate_keys,
    		PULocationID as pickup_point,
    		DOLocationID as dropoff_point
  		FROM 
  			`{}`
		WHERE 
			partitioned_key between'{{ execution_date.strftime("%Y-%m-%d") }}' and '{{ next_execution_date.strftime("%Y-%m-%d") }}'),
   	pickup_data AS (
		SELECT
  			surrogate_keys,
  			zone AS pickup_zone,
  			borough AS pickup_borough
		FROM
  			data_point 
		JOIN
  			`{}`
		ON
  			pickup_point = LocationID ),
    dropoff_data AS (
		SELECT
  			surrogate_keys,
  			zone AS dropoff_zone,
  			borough AS dropoff_borough
		FROM
  			data_point 
		JOIN
  			`{}`
		ON
  			dropoff_point = LocationID)
SELECT 
	surrogate_keys, 
	pickup_zone, 
	pickup_borough, 
	dropoff_zone, 
	dropoff_borough
FROM 
	pickup_data 
JOIN 
	dropoff_data 
USING 
	(surrogate_keys)