-- remove HWM from existing rows that updated
update data_model.customer tgt
set tgt.etl_end_date = dateadd(day, -1, current_date)
    , tgt.etl_current_ind = 'N'
    , tgt.etl_timestamp = current_timestamp
from temp.customer src
where tgt.id = src.id
    and tgt.etl_current_ind = 'Y'
    and md5(tgt.name || tgt.address || tgt.payment_method) != md5(src.name || src.address || src.payment_method);


-- add new rows for updated records with HWM
insert into data_model.customer
select src.etl_key
    , src.id
    , src.name
    , src.address
    , src.payment_method
    , src.etl_start_date
    , src.etl_end_date
    , src.etl_current_ind
    , current_timestamp as etl_timestamp
from temp.customer src
join (select * 
        from data_model.customer where etl_current_ind = 'N' 
        qualify row_number() over (partition by id order by etl_timestamp desc) = 1
    ) tgt 
    on src.id = tgt.id
where md5(tgt.name || tgt.address || tgt.payment_method) != md5(src.name || src.address || src.payment_method);

-- add new rows in the table
insert into data_model.customer
select src.etl_key
    , src.id
    , src.name
    , src.address
    , src.payment_method
    , src.etl_start_date
    , src.etl_end_date
    , src.etl_current_ind
    , current_timestamp as etl_timestamp
from temp.customer src
left join data_model.customer tgt 
    on src.id = tgt.id
where tgt.id is null;


