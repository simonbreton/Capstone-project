from airflow.plugins_manager import AirflowPlugin
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.providers.http.hooks.http import HttpHook
from airflow.models import Variable

import logging
import json
import tenacity

from airflow import models
from airflow.utils import dates


# https://dev.socrata.com/docs/paging.html
class SocrataQueryOperator(BaseOperator):
    """
    Execute execute function.

    Parameters:
    http_conn_id: connection informations for http request 
    method: API call method
    query: SQL query to execute
    resource: url path to query

    """

    template_fields = ["query", "resource"]

    @apply_defaults
    def __init__(
        self,
        http_conn_id="",
        method="",
        query="",
        resource="",
        *args,
        **kwargs
    ):

        super(SocrataQueryOperator, self).__init__(*args, **kwargs)
        self.http_conn_id = http_conn_id
        self.method = method
        self.query = query
        self.resource = resource

    def execute(self, context):

        http_hook = HttpHook(http_conn_id=self.http_conn_id, method=self.method)

        retry_args = dict(
            wait=tenacity.wait_fixed(10), stop=tenacity.stop_after_attempt(10)
        )

        response = http_hook.run_with_advanced_retry(
            endpoint=self.resource, data=self.query, _retry_args=retry_args
        )

        total_record = response.json()[0]["count"]

        # task_instance.xcom_push(key='total_record', value=total_record)
        return total_record
