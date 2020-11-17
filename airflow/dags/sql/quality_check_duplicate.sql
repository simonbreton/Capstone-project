SELECT surrogate_keys,
       count(*)
FROM
  {}
WHERE
  partitioned_key between'{{ execution_date.strftime("%Y-%m-%d") }}' and '{{ next_execution_date.strftime("%Y-%m-%d") }}'
group by surrogate_keys
having count(*) > 1;