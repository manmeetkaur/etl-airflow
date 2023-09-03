-- ingest another table called deleted_entries
select 
    id
    , table_name
    , table_id
    , created_at
    , updated_at
from deleted_entries
{where_cond};


-- change to cdc_load.sql to end date the recods that have been deleted 
update data_model.customer tgt
set tgt.etl_end_date = dateadd(day, -1, current_date)
    , tgt.etl_current_ind = 'N'
    , tgt.etl_timestamp = current_timestamp
from (
        (select table_id from stage.deleted_entries where table_name = 'customer') de
        left join stage.customer c
            on de.table_id = c.id
    ) src
where tgt.id = src.id
    and tgt.etl_current_ind = 'Y';


