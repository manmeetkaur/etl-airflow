create or replace table data_model.customer_bkp
as select * from data_model.customer
; insert overwrite into data_model.customer 
select * from temp.customer;