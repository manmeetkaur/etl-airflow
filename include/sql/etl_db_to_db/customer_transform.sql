truncate table temp.customer

-- new records in OLTP 
;insert into temp.customer(etl_key, id, name, address, payment_method, etl_start_date, etl_end_date, etl_current_ind, etl_timestamp)
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

-- changed records which are already in DWH
;insert into temp.customer(etl_key, id, name, address, payment_method, etl_start_date, etl_end_date, etl_current_ind, etl_timestamp)
select 
    distinct
    md5(tgt.id || current_timestamp) as etl_key
    , coalesce(c.id, tgt.id) as id
    , coalesce(c.name, tgt.name) as name
    , coalesce(ca.address, tgt.address) as address
    , coalesce(cp.payment_method, tgt.payment_method) as payment_method
    , current_date as etl_start_date
    , '9999-12-31' as etl_end_date
    , 'Y' as etl_current_ind 
    , current_timestamp as etl_timestamp
from (select * from data_model.customer tgt where etl_current_ind = 'Y') tgt
left join stage.customer c
    on tgt.id = c.id
left join stage.customer_address ca
    on tgt.id = ca.cust_id
left join stage.customer_payment cp
    on tgt.id = cp.cust_id
where (ca.address is not null or cp.payment_method is not null or c.name is not null);