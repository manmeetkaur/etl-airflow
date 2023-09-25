import logging
import boto3
import botocore
import redshift_connector

from datetime import datetime
from airflow.decorators import dag, task


@dag(schedule="5 12 * * *", start_date=datetime(2021, 12, 1))
def my_data_pipeline():

    logging.basicConfig(level=logging.INFO)

    def create_conn():
        """
        Create and return a Redshift connection object.
        """
        logging.info("Create Redshift connection")
        conn = redshift_connector.connect(
            host='mk-edu.cgelji8gkhy4.us-east-1.redshift.amazonaws.com',
            database='dev',
            port=5439,
            user='awsuser',
            password='redacted'
        )
        return conn

    @task
    def check_source():
        logging.info("Checking source s3")
        s3 = boto3.client('s3'
                          , aws_access_key_id='redacted'
                          , aws_secret_access_key='redacted'
                          , aws_session_token='redacted'
                          , region_name='us-east-1'
                          )
        try:
            s3.head_object(Bucket='mk-edu', Key='incoming/sample.csv')
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                logging.info("File not found")
            else:
                raise

    @task
    def load_data():
        """
        Load data from S3 to Redshift using COPY command.
        """
        logging.info("Loading data from S3 to Redshift")
        sql = """
            copy public.sample(id, name, amount) from 's3://mk-edu/incoming/sample.csv' 
            credentials 'aws_iam_role=arn:aws:iam::532996336208:role/service-role/AmazonRedshift-CommandsAccessRole-20230921T133424' 
            DELIMITER ',' IGNOREHEADER 1;
        """

        conn = create_conn()
        with create_conn() as conn:
            with conn.cursor() as cursor:
                logging.info(f">> Executing {sql}")
                cursor.execute(sql)
            conn.commit()

    @task
    def dq_target():
        logging.info("Checking counts in Redshift")
        sql = "select count(*) as total_count, sum(case when id is null then 1 else 0 end) as null_count from public.sample"
        with create_conn() as conn:
            with conn.cursor() as cursor:
                logging.info(f">> Executing {sql}")
                cursor.execute(sql)
                logging.info(cursor.fetchall())

    logging.info("Start data pipeline")
    check_source() >> load_data() >> dq_target()


my_data_pipeline()
