import boto3
import logging
import json
import decimal
import traceback
from user_service import UserService

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
logging.getLogger("boto3").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)


def lambda_handler(event, context):

    try:

        resource = event["resource"]
        method = event["httpMethod"]

        if "authorizer" in event["requestContext"]:
            user_id = event["requestContext"]["authorizer"]["claims"][
                "cognito:username"
            ]

        us = UserService(event)

        if resource == "/user":

            if method == "POST":
                response, status = us.addUser()

            if method == "GET":
                response, status = us.getUserById(user_id)

            if method == "DELETE":
                pass
            if method == "UPDATE":
                pass

        if resource == "/user/confirm":

            if method == "POST":
                response, status = us.confirm_sign_up()
            if method == "GET":
                pass

        return to_api_response(response, status)

    except Exception as e:
        logging.error(f"[ERROR] - An unkown error occoured - {e}")
        logging.error(traceback.print_exc())


@staticmethod
def to_api_response(response, status):
    return {
        "body": json.dumps(response, default=decimal_default),
        "statusCode": status,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS, PUT, PATCH, DELETE",
            "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent",
        },
    }


@staticmethod
def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError
