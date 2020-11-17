from airflow.hooks.postgres_hook import PostgresHook
from airflow.plugins_manager import AirflowPlugin
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.contrib.hooks.gcs_hook import GoogleCloudStorageHook
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.providers.http.hooks.http import HttpHook
from airflow.models import Variable
import logging

import pandas as pd
import json
import tenacity

from airflow import models
from airflow.utils import dates


# https://dev.socrata.com/docs/paging.html
class SocrataToGCSOperator(BaseOperator):
    """
    Execute execute function.

    Parameters:
    http_conn_id: connection informations for http request 
    google_cloud_storage_conn_id: GCP identification
    bucket_name: gcp bucket name
    object_name: file name to find in the bucket (with the folder path)
    query: query to execute
    method: API call method
    query: SQL query to execute
    resource: url path to query
    partioned_key: partitioned Key as used in production
    max_rows: Max number of rows to get from the API

    """

    template_fields = [
        'bucket_name', 'resource',
        'object_name', 'partitioned_key', 'query', 'max_rows']

    @apply_defaults
    def __init__(
        self,
        http_conn_id='',
        method='',
        google_cloud_storage_conn_id='',
        bucket_name='',
        object_name='',
        query='',
        resource='',
        partitioned_key='',
        max_rows='',
        *args,
        **kwargs):

        super(SocrataToGCSOperator, self).__init__(*args, **kwargs)
        self.http_conn_id = http_conn_id
        self.method = method
        self.google_cloud_storage_conn_id = google_cloud_storage_conn_id
        self.bucket_name = bucket_name
        self.object_name = object_name
        self.query = query
        self.resource = resource
        self.partitioned_key = partitioned_key
        self.max_rows = max_rows

    def execute(self, context):

        http_hook = HttpHook(
            http_conn_id=self.http_conn_id,
            method=self.method
        )

        retry_args = dict(
            wait=tenacity.wait_fixed(10),
            stop=tenacity.stop_after_attempt(10)
        )

        gcp_conn = GCSHook(
            gcp_conn_id=self.google_cloud_storage_conn_id)

        total_rows = int(self.max_rows)

        for offset in range(0, total_rows, 5000):

            q = self.query + f'&$offset={offset}'
            response = http_hook.run_with_advanced_retry(
                endpoint=self.resource,
                data=q,
                _retry_args=retry_args)

            Json_response = response.json()
            df = pd.DataFrame(Json_response)
            df.insert(0, "surrogate_keys", 'null', True)
            df['partitioned_key'] = df[{self.partitioned_key}]
            first_col = df.pop('partitioned_key')
            df.insert(1, 'partitioned_key', first_col)
            df = df.to_csv(index=False)

            name = self.object_name + '/' + str(offset)

            gcp_conn.upload(self.bucket_name, name, data=df)
