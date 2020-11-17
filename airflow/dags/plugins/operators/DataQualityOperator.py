from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import logging


class DataQualityOperator(BaseOperator):
    """
    Execute execute function.

    Parameters:
    gcp_conn_id: gcp connection
    sql: query to execute
    table_list: list of tables on which we want to execute the query
    pass_value: reference value for quality check

    """
    ui_color = '#358140'

    template_fields = ['sql', 'pass_value', 'table_list']

    @apply_defaults
    def __init__(self,
                 gcp_conn_id="",
                 sql="",
                 table_list=[],
                 pass_value="",
                 *args, **kwargs):
        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.gcp_conn_id = gcp_conn_id
        self.sql = sql
        self.table_list = table_list
        self.pass_value = pass_value

    def execute(self, context):
        bq = BigQueryHook(
            gcp_conn_id=self.gcp_conn_id, use_legacy_sql=False)

        total_rows = []

        # self.log.info("{credentials}")
        for table in self.table_list:
            q = self.sql.format(table)
            response = bq.get_pandas_df(q)
            if response.empty:
                response_value = 0
            else:
                response_value = response['f0_'].iloc[0]
            total_rows.append(response_value)

        if sum(total_rows) != self.pass_value:
            logging.info(sum(total_rows))
            logging.info('Tests failed')
            logging.info(total_rows)
            logging.info(self.pass_value)
            raise ValueError('Data quality check failed')
        # self.log.info(f"Success: Copying {self.table} from S3 to Redshift")
