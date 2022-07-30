import boto3
import logging
import json
import decimal
from user_service import UserService

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('boto3').setLevel(logging.CRITICAL)

def lambda_handler(event, context):

    try:
        
        table = boto3.resource('dynamodb').Table('easy_planner_Staging')

        resource = event['resource']
        method = event['httpMethod']
        user_id = event['requestContext']['authorizer']['claims']['cognito:username']
        
        us = UserService(table)

        if resource == "/users":
            pass
        if resource == "/users/{user_id}":
            if method == 'GET':
                response = us.getUsers(user_id)

        return {"body": json.dumps(response, default=decimal_default),
                "statusCode": 200,
                "headers": {
                    'Access-Control-Allow-Origin': "*", 
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS, PUT, PATCH, DELETE', 
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'
                    }
                }

    except Exception as e:
        logging.error(f'Unkown error occoured - {e}')

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError