import boto3
import logging
import json
import decimal
from user_service import UserService, User

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
logging.getLogger("boto3").setLevel(logging.CRITICAL)


def lambda_handler(event, context):

    try:

        resource = event["resource"]
        method = event["httpMethod"]

        if resource == "/user":
            if method == "GET":
                event_user = event["requestContext"]["authorizer"]["claims"]
                user = User(
                    event_user["name"],
                    event_user["family_name"],
                    event_user["email"],
                    event_user["phone_number"],
                )

                response = user.__dict__
                status = 200
        if resource == "/user/{user_id}":
            pass

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
        logging.error(f"Unkown error occoured - {e}")


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError
