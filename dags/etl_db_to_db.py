import os
import logging
from datetime import datetime

from airflow import DAG
from airflow.models import Variable
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

source_tables = ['customer', 'customer_address', 'customer_payment']

with DAG('etl_db_to_db',
            start_date= datetime(2023, 8, 2),
            schedule_interval='@daily', 
            catchup=False,
            template_searchpath=os.path.join(os.getcwd(), 'include', 'sql', 'etl_db_to_db')
        ) as dag:

    @task(multiple_outputs=True)
    def get_dag_conf(**context):
        dag_conf = Variable.get('customer', deserialize_json=True, default_var={})
        load_type = dag_conf.get('load_type', None)
        print(dag_conf)
        print(context['dag_run'].run_type)
        if context['dag_run'].run_type == "scheduled" and load_type == 'full':
            raise ValueError("Full run can't be scheduled!!! Might be left over from a previous run. Aborting...")
        
        if load_type == 'full':
            where_cond = None
        elif load_type == 'delta':
            where_cond = " where updated_at > '{max_date}'"
        else:
            raise ValueError("Invalid load type")

        return {"where_cond": where_cond, "load_type": load_type}

    dag_conf = get_dag_conf()

    @task.branch
    def check_full_load(load_type: str):
        if load_type == 'full':
            return ['full_transform', 'full_load']
        elif load_type == 'delta':
            return ['transform', 'cdc_load']
        
    check_full_load = check_full_load(dag_conf['load_type'])


    full_transform = SQLExecuteQueryOperator(
        task_id='full_transform',
        conn_id='snowflake',
        sql='full_customer_transform.sql',
    )

    full_load = SQLExecuteQueryOperator(
        task_id='full_load',
        conn_id='snowflake',
        sql='full_load.sql'
    )

    transform = SQLExecuteQueryOperator(
        task_id='transform',
        conn_id='snowflake',
        sql='customer_transform.sql',
    )

    cdc_load = SQLExecuteQueryOperator(
        task_id='cdc_load',
        conn_id='snowflake',
        sql='cdc_load.sql',
        split_statements=True
    )

    for source_table in source_tables:

        @task(task_id=f'{source_table}_extract')
        def extract(source_table: str, dag_conf: dict):
            pg_hook = PostgresHook(
                schema='postgres',
                postgres_conn_id='postgres',
            )

            with open(os.path.join(os.getcwd(), 'include', 'sql', f'{source_table}.sql'), 'r') as sql_file:
                sql = sql_file.read()

            out_file = os.path.join(os.getcwd(), 'include', 'data', f'{source_table}.csv')
            if dag_conf['load_type'] == 'full':
                logging.info(f"Load Type: {dag_conf['load_type']}")
                sql = f"COPY {source_table} TO STDOUT WITH CSV DELIMITER ','"
            else:
                logging.info(f"Load Type: {dag_conf['load_type']}")
                max_updated = Variable.get(f'{source_table}_max_updated')
                if not max_updated:
                    raise ValueError("MAX updated_at not found for Delta load! Aborting...")
                sql = sql.format(where_cond=dag_conf['where_cond']).format(max_date=max_updated)
                logging.info(sql)
                sql = f"COPY ({sql}) TO STDOUT WITH CSV DELIMITER ','"
            pg_hook.copy_expert(sql, out_file)
            
            s3_conn = S3Hook(aws_conn_id='aws')
            s3_conn.load_file(filename=out_file, key=f'pg_data/{source_table}.csv', bucket_name='mk-edu', replace=True)

        stage = SQLExecuteQueryOperator(
            task_id=f'load_{source_table}',
            conn_id='snowflake',
            sql='stage.sql',
            split_statements=True,
            params={"source_table": source_table}
        )

        @task(task_id=f"{source_table}_get_max_date")
        def collect_metadata(source_table):
            
            sf_hook = SnowflakeHook(
                snowflake_conn_id='snowflake'
            )
            with open(os.path.join(os.getcwd(), 'include', 'sql', 'get_max_date.sql'), 'r') as f:
                sql = f.read()
            sql = sql.format(stage_table=source_table)
            data = sf_hook.run(sql=sql, handler=lambda result_set: result_set.fetchall()[0][0])
            if data:
                Variable.set(f'{source_table}_max_updated', data.strftime('%Y-%m-%d %H:%M:%S.%f'))

        extract(source_table, dag_conf) >> stage >> collect_metadata(source_table) >> check_full_load >> full_transform >> full_load
        check_full_load >> transform >> cdc_load
