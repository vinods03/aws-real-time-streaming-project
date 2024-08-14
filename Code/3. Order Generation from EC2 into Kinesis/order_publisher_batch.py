import boto3
import logging
import json
import time
import sys
from order_generator import make_order

logging.basicConfig(
  format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
  datefmt='%Y-%m-%d %H:%M:%S',
  level=logging.INFO,
  handlers=[
      logging.FileHandler("producer.log"),
      logging.StreamHandler(sys.stdout)
  ]
)

kinesis = boto3.client('kinesis',region_name='us-east-1')

def publish_order(args):

    stream_name = args[1]
    orders = []
    batch_number = 1
    num_records = 0

    logging.info(f"Starting to write into the kinesis data stream {stream_name} in batches of {args[2]}")
    
    while True:

        order = make_order()
        kwargs = {'Data': json.dumps(order).encode('utf-8'), 'PartitionKey': order['order_id']}
        orders.append(kwargs)

        if len(orders) > int(args[2]):
            
            try:
                response = kinesis.put_records(StreamName = stream_name, Records = orders)
                logging.info(f"Successfully published batch number {batch_number} into the kinesis stream {stream_name}")

                # Even though we have published a batch of records, we can grab the errors, if any, at individual record level
                for i, record_response in enumerate(response['Records']):

                    error_code = record_response.get('ErrorCode')
                    if error_code:
                        logging.error(f"Failed to publish order {orders[i]['Data']}. The error_code is {error_code}")
                        
                    # logging.info(f"The value of i is {i}")
                    
                num_records = num_records + i
                logging.info(f"The number of records published till batch number {batch_number} is {num_records}")

                orders = [] # this resetting is needed to make sure we send 20 or whatever number of records we need to send in each batch

            except Exception as e:
                logging.error(f"Publish into kinesis data stream {stream_name} failed with exception {e}")

            time.sleep(10)
            batch_number = batch_number + 1

if __name__ == '__main__':
    publish_order(sys.argv)
