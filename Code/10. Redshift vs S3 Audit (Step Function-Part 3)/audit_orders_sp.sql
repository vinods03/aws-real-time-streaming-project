CREATE OR REPLACE PROCEDURE dev.audit_orders_sp ()
AS $$
BEGIN

 RAISE INFO 'STARTING THE LOAD INTO dev.orders_audit';

INSERT into dev.orders_audit
select a.*, 'NEW' from
(
select run_id, order_id, customer_id, seller_id, product_code, product_name, product_price, product_qty, order_ts
from s3_staging_schema.new_orders_staging_area 
) a
full outer JOIN
(
select run_id, order_id, customer_id, seller_id, product_code, product_name, product_price, product_qty, order_ts
from dev.orders_final 
) b
on a.run_id = b.run_id
and a.order_id = b.order_id
where a.customer_id <> b.customer_id
and a.seller_id <> b.seller_id
and a.product_code <> b.product_code
and a.product_name <> b.product_name
and a.product_price <> b.product_price
and a.product_qty <> b.product_qty
and a.order_ts <> b.order_ts;

commit;

RAISE INFO 'COMPLETED THE LOAD INTO dev.ordersaudit';

EXCEPTION 
 
 WHEN OTHERS THEN
 RAISE EXCEPTION 'LOAD INTO dev.orders_audit failed';
 
END;
$$ LANGUAGE plpgsql;
