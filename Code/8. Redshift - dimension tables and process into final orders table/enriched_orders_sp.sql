CREATE OR REPLACE PROCEDURE dev.enriched_orders_sp ()
AS $$
BEGIN

 RAISE INFO 'STARTING THE LOAD INTO dev.orders_final';

 INSERT INTO dev.orders_temp
 select run_id, order_id, customer_id, seller_id, product_code, product_name, product_price, product_qty, order_ts
 from dev.orders stg
 where stg.run_id not in (select distinct run_id from dev.orders_final);

 INSERT INTO dev.orders_final
 select run_id, order_id, a.customer_id, customer_name, customer_address, a.seller_id, seller_name, seller_address, product_code, product_name, product_price, product_qty, order_ts from dev.orders_temp a left outer join dev.customers b
 on a.customer_id = b.customer_id
 left outer join dev.sellers c
 on a.seller_id = c.seller_id;

 COMMIT;
 
 TRUNCATE TABLE dev.orders_temp;

 RAISE INFO 'COMPLETED THE LOAD INTO dev.orders_final';

EXCEPTION 
 
 WHEN OTHERS THEN
 RAISE EXCEPTION 'LOAD INTO dev.orders_final failed';
 
END;
$$ LANGUAGE plpgsql;
