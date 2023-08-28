-- Initial setup - first day
create table public.customer(id int, name varchar, created_at timestamp, updated_at timestamp);

create table public.customer_address(id int, cust_id int, address varchar, created_at timestamp, updated_at timestamp);

create table public.customer_payment(id int, cust_id int, payment_method varchar, created_at timestamp, updated_at timestamp);

insert into customer(id, name, created_at, updated_at)
values(111, 'Manmeet', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

insert into customer(id, name, created_at, updated_at)
values(112, 'Jaideep', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

insert into customer_address(id, cust_id, address, created_at, updated_at)
values(123, 111, 'my_address_1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

insert into customer_address(id, cust_id, address, created_at, updated_at)
values(124, 112, 'his_address_1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

insert into customer_payment(id, cust_id, payment_method, created_at, updated_at)
values(321, 111, 'visa', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

insert into customer_payment(id, cust_id, payment_method, created_at, updated_at)
values(322, 112, 'amex', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);


-- second day

insert into customer(id, name, created_at, updated_at)
values(113, 'Jasmeher', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

insert into customer_address(id, cust_id, address, created_at, updated_at)
values(125, 113, 'her_address_1', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

insert into customer_payment(id, cust_id, payment_method, created_at, updated_at)
values(323, 113, 'mastercard', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

update customer_address 
set address = 'my_address_2'
, updated_at = CURRENT_TIMESTAMP
where id = 123;


-- third day

update customer_address 
set address = 'his_address_1'
, updated_at = CURRENT_TIMESTAMP
where id = 124;

update customer_payment
set payment_method = 'mastercard'
, updated_at = CURRENT_TIMESTAMP
where id = 321;

-- fourth day

update customer_address 
set address = 'her_address_2'
, updated_at = CURRENT_TIMESTAMP
where id = 125;

insert into customer(id, name, created_at, updated_at)
values(114, 'Nivi', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

insert into customer_address(id, cust_id, address, created_at, updated_at)
values(126, 114, 'her_address', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

insert into customer_payment(id, cust_id, payment_method, created_at, updated_at)
values(324, 114, 'one', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);