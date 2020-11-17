from airflow import DAG
from datetime import datetime
from datetime import timedelta
from airflow.models import Variable
from airflow import models

from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator
from operators.SocrataToGCSOperator import SocrataToGCSOperator
from operators.SocrataQueryOperator import SocrataQueryOperator
from operators.DataQualityOperator import DataQualityOperator
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryCreateEmptyDatasetOperator,
    BigQueryInsertJobOperator,
)
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import (
    GCSToBigQueryOperator,
)

import os
import logging

# requiered to handle service error authentification 
os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"
] = "~/service_account_key.json"

environement_variables = Variable.get("env", deserialize_json=True)
ressources_table_destination = "data-engineering-capstone.Ressources.nyc_taxi_zones"
dataset_metadata = Variable.get("metadata", deserialize_json=True)

stg_dataset_name = environement_variables["stg"]
stg_table_name = environement_variables["raw_data"]


def set_parameters(ds, **kwargs):

    task_instance = kwargs["task_instance"]
    execution_year = kwargs["execution_date"].strftime("%Y")
    first_year = next(iter(dataset_metadata))
    parameters = list(dataset_metadata[first_year].keys())

    for param in parameters:
        value = dataset_metadata[f"{execution_year}"][param]
        task_instance.xcom_push(key=param, value=value)


def return_branch(ds, **kwargs):
    execution_year = kwargs["execution_date"].strftime("%Y")
    geo_type = dataset_metadata[f"{execution_year}"]["geoType"]
    if geo_type == "coordinate":
        return "geo_coordinate_query"
    return "geo_location_query"


default_args = {
    "owner": "simon",
    "depends_on_past": False,
    "retries": 10,
    "retry_delay": timedelta(minutes=1),
    "catchup": True,
    "email_on_retry": False,
}

dag = DAG(
    "ELT",
    default_args=default_args,
    description="ELT Historical NY Yellow Taxi Cab Data",
    schedule_interval="@daily",
    start_date=datetime(2015, 12, 1),
    end_date=datetime(2015, 12, 3),
    template_searchpath=["airflow_home/dags/sql"],
)

start = DummyOperator(task_id="start", retries=2, dag=dag)

call_parameters = PythonOperator(
    task_id="call_parameters",
    provide_context=True,
    python_callable=set_parameters,
    dag=dag,
)

total_record = SocrataQueryOperator(
    task_id="total_record",
    http_conn_id="data_cityofnewyork",
    method="GET",
    google_cloud_storage_conn_id="google_cloud_default",
    resource="{{ task_instance.xcom_pull(task_ids='call_parameters', key='endPoint') }}",
    query="{% include 'total_record.sql' %}",
    dag=dag,
)

extract_data_from_socrata_to_gcs = SocrataToGCSOperator(
    task_id="extract_data_from_socrata_to_gcs",
    http_conn_id="data_cityofnewyork",
    method="GET",
    google_cloud_storage_conn_id="google_cloud_default",
    resource="{{ task_instance.xcom_pull(task_ids='call_parameters', key='endPoint') }}",
    object_name='data/{{execution_date.strftime("%Y") }}/{{execution_date.strftime("%m") }}/{{execution_date.strftime("%d") }}',
    bucket_name="{{ var.json.env.bucket }}",
    partitioned_key="{{ task_instance.xcom_pull(task_ids='call_parameters', key='pickup_dimension_name') }}",
    query="{% include 'api_params.sql' %}",
    max_rows="{{ task_instance.xcom_pull(task_ids='total_record', key='return_value') }}",
    dag=dag,
)

create_staging_dataset = BigQueryCreateEmptyDatasetOperator(
    task_id="create_staging_dataset",
    gcp_conn_id="my_gcp_connection",
    dataset_id="{{ var.json.env.stg }}",
    dag=dag,
)

create_production_dataset = BigQueryCreateEmptyDatasetOperator(
    task_id="create_production_dataset",
    gcp_conn_id="my_gcp_connection",
    dataset_id="{{ var.json.env.production }}",
    dag=dag,
)

create_fact_table = BigQueryInsertJobOperator(
    task_id="create_fact_table",
    configuration={
        "query": {
            "query": "{% include 'create_fact_table.sql' %}",
            "use_legacy_sql": False,
        }
    },
    dag=dag,
)

create_geo_table = BigQueryInsertJobOperator(
    task_id="create_geo_table",
    configuration={
        "query": {
            "query": "{% include 'create_geo_table.sql' %}",
            "use_legacy_sql": False,
        }
    },
    dag=dag,
)

create_summary_table = BigQueryInsertJobOperator(
    task_id="create_summary_table",
    configuration={
        "query": {
            "query": "{% include 'create_summary_table.sql' %}",
            "use_legacy_sql": False,
        }
    },
    dag=dag,
)

create_bad_row_table = BigQueryInsertJobOperator(
    task_id="create_bad_row_table",
    configuration={
        "query": {
            "query": "{% include 'create_bad_row_table.sql' %}",
            "use_legacy_sql": False,
        }
    },
    dag=dag,
)

load_data_from_gsc_to_bigquery = GCSToBigQueryOperator(
    task_id="load_data_from_gsc_to_bigquery",
    bucket="{{ var.json.env.bucket }}",
    source_objects=[
        'data/{{execution_date.strftime("%Y") }}/{{execution_date.strftime("%m") }}/{{execution_date.strftime("%d") }}*'
    ],
    destination_project_dataset_table=f"{stg_dataset_name}.{stg_table_name}",
    skip_leading_rows=1,
    source_format="CSV",
    create_disposition="CREATE_IF_NEEDED",
    write_disposition="WRITE_APPEND",
    schema_update_options=["ALLOW_FIELD_RELAXATION", "ALLOW_FIELD_ADDITION"],
    autodetect=True,
    dag=dag,
)

quality_check = DataQualityOperator(
    task_id="quality_check",
    provide_context=True,
    gcp_conn_id="google_cloud_default",
    sql='{% include "quality_check.sql" %}',
    table_list=[
        "{{ var.json.env.project }}.{{ var.json.env.stg }}.{{ var.json.env.raw_data }}"
    ],
    pass_value="{{ task_instance.xcom_pull(task_ids='get_max_record', key='return_value') }}",
    dag=dag,
)

insert_skey = BigQueryInsertJobOperator(
    task_id="insert_skey",
    configuration={
        "query": {"query": "{% include 'insert_key.sql' %}", "useLegacySql": False}
    },
    dag=dag,
)

fact_query = BigQueryInsertJobOperator(
    task_id="fact_query",
    configuration={
        "query": {"query": "{% include 'fact_query.sql' %}", "use_legacy_sql": False}
    },
    dag=dag,
)

branching = BranchPythonOperator(
    task_id="branching",
    python_callable=return_branch,
    trigger_rule="all_done",
    provide_context=True,
)

geo_coordinate_query = BigQueryInsertJobOperator(
    task_id="geo_coordinate_query",
    configuration={
        "query": {"query": "{% include 'coordinate.sql' %}", "use_legacy_sql": False}
    },
    dag=dag,
)

geo_location_query = BigQueryInsertJobOperator(
    task_id="geo_location_query",
    configuration={
        "query": {"query": "{% include 'location.sql' %}", "use_legacy_sql": False}
    },
    dag=dag,
)

quality_check_duplicate = DataQualityOperator(
    task_id="quality_check_duplicate",
    provide_context=True,
    gcp_conn_id="google_cloud_default",
    sql='{% include "quality_check_duplicate.sql" %}',
    table_list=[
        "{{ var.json.env.project }}.{{ var.json.env.production }}.{{ var.json.env.fact }}"
    ],
    pass_value=0,
    dag=dag,
)

summary_query = BigQueryInsertJobOperator(
    task_id="summary_query",
    configuration={
        "query": {"query": "{% include 'summary.sql' %}", "use_legacy_sql": False}
    },
    dag=dag,
)

bad_rows_query = BigQueryInsertJobOperator(
    task_id="bad_rows_query",
    configuration={
        "query": {"query": "{% include 'bad_rows.sql' %}", "use_legacy_sql": False}
    },
    dag=dag,
)

stop = DummyOperator(task_id="stop", retries=2, dag=dag)

start >> call_parameters
call_parameters >> [total_record, create_production_dataset, create_staging_dataset]
create_staging_dataset >> create_bad_row_table
create_production_dataset >> [create_fact_table, create_geo_table, create_summary_table]
create_summary_table >> summary_query
create_fact_table >> fact_query
create_geo_table >> branching
create_bad_row_table >> bad_rows_query
total_record >> extract_data_from_socrata_to_gcs
[
    extract_data_from_socrata_to_gcs,
    create_staging_dataset,
] >> load_data_from_gsc_to_bigquery >> quality_check
quality_check >> insert_skey >> [fact_query, branching, bad_rows_query]
call_parameters >> branching >> [geo_coordinate_query, geo_location_query]
fact_query >> quality_check_duplicate
[
    quality_check_duplicate,
    geo_coordinate_query,
    geo_location_query,
] >> summary_query >> stop
