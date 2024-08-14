from pyspark.sql import SparkSession

import boto3
import json
sm_client = boto3.client('secretsmanager')
secret_value = sm_client.get_secret_value(SecretId='redshift-cluster-secret')
credentials = json.loads(secret_value['SecretString'])

username = credentials['username']
password = credentials['password']
host = credentials['host']
port = credentials['port']
database = credentials['dbname']
url = f"jdbc:redshift://{host}:{port}/{database}?user={username}&password={password}"
print('The url is: ', url)

# With this spark session, we will not be able to read glue data catalog
# spark.sql('show databases').show(truncate=False) -> will not return any glue database
# spark = SparkSession.builder.appName('OrderRedshiftLoader').getOrCreate()

# With this spark session, we will be able to connect to the glue data catalog
# spark.sql('show databases').show(truncate=False) -> will  return glue databases
spark = SparkSession.builder.config("hive.metastore.client.factory.class","com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory") \
.enableHiveSupport() \
.appName('OrderRedshiftLoader') \
.getOrCreate()

# test sql for spark session creation
spark.sql('select current_date()').show()

# test sql for glue data catalog connection
spark.sql('show databases').show(truncate=False)

# we will have a checkpoint table in redshift for orders that stores the max timestamp from the source glue data catalog table
# any record with timestamp greater than this will be picked from glue data catalog table for the subsequent processing
# we are using the checkpoint table instead of the main orders table as a performance improvement feature
# the checkpoint table will have just 1 row with latest timestamp
# we dont have to read the huge redshift table and perform a max timestamp on it, by using this approach
redshift_orders_chkpoint_df = spark.read \
.format('io.github.spark_redshift_community.spark.redshift') \
.option('aws_iam_role', 'arn:aws:iam::100163808729:role/MyRedshiftRoleWithAdminAccess') \
.option('url', url) \
.option('dbtable', 'dev.orders_chkpoint') \
.option('tempdir', 's3://real-time-streaming-project-vinod/tempdir-for-redshift-processing/read/') \
.load()

print('####################redshift_orders_chkpoint_df$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
redshift_orders_chkpoint_df.show()
redshift_orders_chkpoint_df.createOrReplaceGlobalTempView("redshift_orders_chkpoint")

# read from source glue data catalog
# read only those records with timestamp greater than the timestamp in the checkpoint orders table
# the ">" logic will only work for non-empty target redshift table, hence the if-else condition
if (redshift_orders_chkpoint_df.count() > 0):
    # print('If part')
    orders_df = spark.sql("""select run_id,
    order_id,
    customer_id,
    seller_id,
    product_code,
    product_name,
    product_price,
    product_qty,
    order_ts from `ecommerce-database`.`new_orders_staging_area`
    where order_ts > (select max_order_ts from global_temp.redshift_orders_chkpoint)""")
else:
    # print('Else part')
    orders_df = spark.sql("""select run_id,
    order_id,
    customer_id,
    seller_id,
    product_code,
    product_name,
    product_price,
    product_qty,
    order_ts from `ecommerce-database`.`new_orders_staging_area`""")

# orders_df.show()
# write the incremental records from source glue data catalog table into the main redshift orders table
orders_df.write \
.mode('append') \
.format('io.github.spark_redshift_community.spark.redshift') \
.option('aws_iam_role', 'arn:aws:iam::100163808729:role/MyRedshiftRoleWithAdminAccess') \
.option('url', url) \
.option('dbtable', 'dev.orders') \
.option('tempdir', 's3://real-time-streaming-project-vinod/tempdir-for-redshift-processing/') \
.save()

# here is where we retrieve the max timestamp in the source glue data catalog table for the current process
orders_max_ts_df = spark.sql("""select 
max(order_ts) as max_order_ts from `ecommerce-database`.`new_orders_staging_area`
""")

# we store the max timestamp in the source glue data catalog table for the current process in the checkpoint table
# we overwrite here, unlike append in the main orders table
orders_max_ts_df.write \
.mode('overwrite') \
.format('io.github.spark_redshift_community.spark.redshift') \
.option('aws_iam_role', 'arn:aws:iam::100163808729:role/MyRedshiftRoleWithAdminAccess') \
.option('url', url) \
.option('dbtable', 'dev.orders_chkpoint') \
.option('tempdir', 's3://real-time-streaming-project-vinod/tempdir-for-redshift-processing/') \
.save()

