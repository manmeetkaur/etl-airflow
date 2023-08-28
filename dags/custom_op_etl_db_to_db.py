import os
from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from include.operators.app_operators import ExtractOperator, CollectMetdataOperator, GetDAGConfOperator

source_tables = ['customer', 'customer_address', 'customer_payment']

with DAG('custom_op_etl_db_to_db',
            start_date= datetime(2023, 8, 2),
            schedule_interval='@daily', 
            catchup=False,
            template_searchpath=os.path.join(os.getcwd(), 'include', 'sql', 'etl_db_to_db')
        ) as dag:
  
    dag_conf = GetDAGConfOperator(
        task_id='get_dag_conf'
    )

    @task.branch
    def check_full_load(**context):
        load_type = context['ti'].xcom_pull(task_ids='get_dag_conf')['load_type']
        print(load_type)
        if load_type == 'full':
            return ['full_transform', 'full_load']
        elif load_type == 'delta':
            return ['transform', 'cdc_load']
        
    check_load_type = check_full_load()
        
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

        extract = ExtractOperator(
            task_id=f'{source_table}_extract',
            source_table=source_table,
            load_type="{{ ti.xcom_pull(task_ids='get_dag_conf', key='load_type') }}",
            where_cond="{{ ti.xcom_pull(task_ids='get_dag_conf', key='where_cond') }}"
        )

        stage = SQLExecuteQueryOperator(
            task_id=f'load_{source_table}',
            conn_id='snowflake',
            sql='stage.sql',
            split_statements=True,
            params={"source_table": source_table}
        )

        collect_metadata = CollectMetdataOperator(
            task_id=f"{source_table}_get_max_date",
            source_table=source_table
        )

        dag_conf >> extract >> stage >> collect_metadata >> check_load_type >> full_transform >> full_load
        check_load_type >> transform >> cdc_load
