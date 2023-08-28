select 
    id
    , cust_id
    , payment_method
    , created_at
    , updated_at
from public.customer_payment
{where_cond}