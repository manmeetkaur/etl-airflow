from datetime import datetime, timedelta
import os 
import json
import logging
from typing import Any, Iterable
from airflow.models import Variable
from airflow.models.baseoperator import BaseOperator
from airflow.models.dag import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.utils.context import Context
from airflow.utils.task_group import TaskGroup


class ExtractOperator(BaseOperator):

    template_fields = ['load_type', 'where_cond']

    def __init__(self, source_table: str, where_cond: str, load_type: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_table = source_table
        self.where_cond = where_cond
        self.load_type = load_type

    def execute(self, context: Context) -> Any:
        pg_hook = PostgresHook(
            schema='postgres',
            postgres_conn_id='postgres',
        )
        print("here", self.where_cond)
        print("here", self.load_type)
        with open(os.path.join(os.getcwd(), 'include', 'sql', f'{self.source_table}.sql'), 'r') as sql_file:
            sql = sql_file.read()

        out_file = os.path.join(os.getcwd(), 'include', 'data', f'{self.source_table}.csv')

        logging.info(self.load_type)
        if self.load_type == 'full':
            logging.info(f"Load Type: {self.load_type}")
            sql = f"COPY {self.source_table} TO STDOUT WITH CSV DELIMITER ','"
        else:
            logging.info(f"Load Type: {self.load_type}")
            max_updated = Variable.get(f'{self.source_table}_max_updated')
            if not max_updated:
                raise ValueError("MAX updated_at not found for Delta load! Aborting...")
            sql = sql.format(where_cond=self.where_cond).format(max_date=max_updated)
            logging.info(sql)
            sql = f"COPY ({sql}) TO STDOUT WITH CSV DELIMITER ','"
        pg_hook.copy_expert(sql, out_file)
        
        s3_conn = S3Hook(aws_conn_id='aws')
        s3_conn.load_file(filename=out_file, key=f'pg_data/{self.source_table}.csv', bucket_name='mk-edu', replace=True)


class CollectMetdataOperator(BaseOperator):
    def __init__(self, source_table: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_table = source_table

    def execute(self, context: Context) -> Any:
        sf_hook = SnowflakeHook(
            snowflake_conn_id='snowflake'
        )
        with open(os.path.join(os.getcwd(), 'include', 'sql', 'get_max_date.sql'), 'r') as f:
            sql = f.read()
        sql = sql.format(stage_table=self.source_table)
        data = sf_hook.run(sql=sql, handler=lambda result_set: result_set.fetchall()[0][0])
        if data:
            Variable.set(f'{self.source_table}_max_updated', data.strftime('%Y-%m-%d %H:%M:%S.%f'))


class GetDAGConfOperator(BaseOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self, context: Context) -> Any:
        dag_conf = Variable.get('customer', deserialize_json=True, default_var={})
        load_type = dag_conf.get('load_type', None)
        logging.info(dag_conf)
        logging.info(context['dag_run'].run_type)

        if context['dag_run'].run_type == "scheduled" and load_type == 'full':
            raise ValueError("Full run can't be scheduled!!! Might be left over from a previous run. Aborting...")
        
        if load_type == 'full':
            where_cond = None
        elif load_type == 'delta':
            where_cond = " where updated_at > '{max_date}'"
        else:
            raise ValueError("Invalid load type")

        return {"where_cond": where_cond, "load_type": load_type}
