
-- change to customer_transfrorm.sql to only get new records
insert into temp.customer(etl_key, id, name, address, payment_method, etl_start_date, etl_end_date, etl_current_ind, etl_timestamp)
select 
    md5(c.id || current_timestamp) as etl_key
    , c.id
    , c.name
    , ca.address
    , cp.payment_method
    , current_date as etl_start_date
    , '9999-12-31' as etl_end_date
    , 'Y' as etl_current_ind 
    , current_timestamp as etl_timestamp
from stage.customer c
left join stage.customer_address ca
    on c.id = ca.cust_id
left join stage.customer_payment cp
    on c.id = cp.cust_id
where c.deleted_at is null;

-- change to cdc_load.sql to end date the recods that have been deleted 
update data_model.customer tgt
set tgt.etl_end_date = dateadd(day, -1, current_date)
    , tgt.etl_current_ind = 'N'
    , tgt.etl_timestamp = current_timestamp
from stage.customer src
where tgt.id = src.id
    and tgt.etl_current_ind = 'Y'
    and src.deleted_at is not null;