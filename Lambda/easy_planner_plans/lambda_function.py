import boto3
import logging
import json
import decimal
from plan_service import PlanService

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('boto3').setLevel(logging.CRITICAL)

def lambda_handler(event, context):

    try:
        
        print(event)
        table = boto3.resource('dynamodb').Table('easy_planner_Staging')

        resource = event['resource']
        method = event['httpMethod']
        user_id = event['requestContext']['authorizer']['claims']['cognito:username']

        ps = PlanService(table, user_id)

        if resource == "/plans":
            if method == "GET":
                response, status = ps.getPlans()
            if method == "POST":
                body = json.loads(event['body'])
                response, status = ps.createPlan(body)
        if resource == "/plans/{plan_id}":
            plan_id = event['pathParameters']['plan_id']
            if method == "GET":
                response, status = ps.getPlanById(plan_id)
            if method == "DELETE":
                response, status = ps.deletePlan(plan_id)
            if method == "PUT":
                body = json.loads(event['body'])
                response, status = ps.updatePlan(plan_id, body)

        return {"body": json.dumps(response, default=decimal_default),
                "statusCode": status,
                "headers": {
                    'Access-Control-Allow-Origin': "*", 
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS, PUT, PATCH, DELETE', 
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent'
                    }
                }
    except Exception as e:
        logging.error(f'Unknown error occoured - {e}')

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError