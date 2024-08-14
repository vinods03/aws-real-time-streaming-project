import json
import boto3
import time

redshift_client = boto3.client('redshift-data')
secrets_manager_client = boto3.client('secretsmanager')
sns_client = boto3.client('sns')

secret_value = secrets_manager_client.get_secret_value(SecretId='redshift-cluster-secret')
redshift_credentials = json.loads(secret_value['SecretString'])
query_str = "select * from dev.orders_audit where status='NEW'"

def lambda_handler(event, context):
    
    try:
        
        execute_response = redshift_client.execute_statement(
        ClusterIdentifier='redshift-cluster-1',
        Database=redshift_credentials['dbname'],
        DbUser=redshift_credentials['username'],
        Sql=query_str)
        print('Redshift execute statement is successful')
        # print('The execute response is ', execute_response)
        
        query_id = execute_response['Id']
        print('The redshift query id is: ', query_id)
        
        while (redshift_client.describe_statement(Id=query_id)['Status'] != 'FINISHED'):
            # print(redshift_client.describe_statement(Id=query_id))
            # print(redshift_client.describe_statement(Id=query_id)['Status'])
            # print(redshift_client.describe_statement(Id=query_id)['ResultRows'])
            time.sleep(5)
            
        print('The status of redshift query is: ', redshift_client.describe_statement(Id=query_id)['Status'])
        # print(redshift_client.describe_statement(Id=query_id)['ResultRows'])
        
        try:
            get_response = redshift_client.get_statement_result(Id=query_id)
            print('The get response is ', get_response['Records'])
        except Exception as e:
            print('The Redshift get statement result failed with the exception: ', e)
        
        for record in get_response['Records']:
            # print('The record is: ', record)
            # print('The run id is: ', record[0]['longValue'])
            run_id = record[0]['longValue']
            
            try: 
                sns_response = sns_client.publish(
                TopicArn='arn:aws:sns:us-east-1:100163808729:new-orders-topic',
                Message='Mismatch between S3 staging and Redshift for the run id '+str(run_id),
                Subject='S3 Staging vs Redshift mismatch')
                print('The sns response is: ',sns_response)
            except Exception as e:
                print('Mismatch notification failed with the exception: ', e)
            
    except Exception as e:
        print('Redshift execute statement failed with exception ',e)
    
