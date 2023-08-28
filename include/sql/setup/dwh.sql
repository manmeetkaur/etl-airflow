-- snowflake S3 stage
create or replace stage postgre_ext_stage url='s3://mk-edu/pg_data/'
credentials=(aws_key_id='MKIAXYGIOVEXAMPLE' aws_secret_key='H9exampleG4r9jMKhkee0aMKDywEXAMPLE0CN');

-- stage tables
create table stage.customer (id int, name string, created_at timestamp, updated_at timestamp);
create table stage.customer_address (id int, cust_id int, address string, created_at timestamp, updated_at timestamp);
create table stage.customer_payment (id int, cust_id int, payment_method string, created_at timestamp, updated_at timestamp);

-- temp transform table
create or replace table demo.temp.customer(etl_key string, id int, name string, address string, payment_method string, etl_start_date date, etl_end_date date, etl_current_ind char(1), etl_timestamp current_timestamp);

-- final reporting table
create or replace table demo.data_model.customer(etl_key string, id int, name string, address string, payment_method string, etl_start_date date, etl_end_date date, etl_current_ind char(1), etl_timestamp current_timestamp);