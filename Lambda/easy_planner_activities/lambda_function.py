import boto3
import logging
import json
import decimal
from activity_service import ActivityService

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
logging.getLogger("boto3").setLevel(logging.CRITICAL)


def lambda_handler(event, context):

    try:

        resource = event["resource"]
        method = event["httpMethod"]
        user_id = event["requestContext"]["authorizer"]["claims"]["cognito:username"]

        acs = ActivityService(user_id)

        if resource == "activities":
            if method == "GET":
                response, status = acs.get_user_activities()
            if method == "POST":
                response, status = acs.add_activity()
        if resource == "activities/{activity_id}":
            activity_id = event["pathParameters"]["activity_id"]

            if method == "GET":
                response, status = acs.get_user_activity_by_id(activity_id)
            if method == "DELETE":
                response, status = acs.delete_activity(activity_id)
            if method == "PUT":
                response, status = acs.update_activity(activity_id)

        return {
            "body": json.dumps(response, default=decimal_default),
            "statusCode": status,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS, PUT, PATCH, DELETE",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent",
            },
        }

    except Exception as e:
        logging.error(f"[ERROR] - Unkown error - {e}")
        raise Exception


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError
