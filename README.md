## Setup an Airflow project on your local

1. Install Astro CLI using brew install astro
2. Initialize an Airflow project using astro dev init
3. Start your local Airflow environment using astro dev start

For detailed instructions, see [Astro CLI docs](https://docs.astronomer.io/astro/cli/overview).

## Assuming the following details about our data stack:

**Source database:** PostgreSQL
**Target database:** Snowflake
**Sync Frequency:** Inter-day (Batch)
**Source tables:** customer, customer_address, customer_payment
**Target table:** customer
**Sync type:** Full sync followed by daily incremental syncs based on a timestamp column in source, updated_at
**SCD Type:** Target table is a SCD Type 2

### Example pipeline - etl_db_to_db.py

Setup SQL in: `include/setup/`

DAG sql in: `include/etl_db_to_db/`

### Variable for the example pipeline looks like:

```
{
"load_type": "full",
"source_tables": ["customer", "customer_address", "customer_payment"]
}
```

### Connections used

snowflake=`snowflake://<YOURUSER>:<YOURPASSWORD>/<YOUR-SCHEMA>?__extra__=%7B%22account%22%3A+%22<YOUR-ACCOUNT>%22%2C+%22warehouse%22%3A+%22<YOUR-WAREHOUSE>%22%2C+%22database%22%3A+%22<YOUR-DATABASE>%22%2C+%22region%22%3A+%22<YOUR-REGION>%22%2C+%22role%22%3A+%22<YOUR-ROLE>%22%2C+%22insecure_mode%22%3A+false%7D`
aws=`aws://<YOUR_ACCESS_ID>:<YOUR_SECRET_KEY>@`
postgres=`postgres://<YOUR_POSTGRES_USER>:<YOURPASSWORD>@<YOUR-RDS-NAME>.<YOUR-RDS-ID>.<YOUR-REGION>.rds.amazonaws.com:5432/<YOUR-DATABASE>?__extra__=%7B%7D^`
