import logging
import boto3
import os
from boto3.dynamodb.conditions import Key


class ActivityService:
    def __init__(self, user_id):
        self.user_id = user_id
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.table = os.getenv("table")
        self.dynamodb = boto3.resource("dynamodb").Table(self.table)

    def get_user_activities_by_plan(self, plan_id):

        key_expression = Key("PK").eq(f"Plan#{plan_id}") & Key("SK").begins_with(
            "Activity"
        )

        try:
            response = self.dynamodb.query(KeyConditionExpression=key_expression)
        except Exception as e:
            self.logger.error(f"[ERROR] - Unkown error when calling activities - {e}")

        if "Items" in response:
            return response["Items"], 200
        else:
            return {}, 204

    def get_user_activity_by_id(self, activity_id):
        return "", ""

    def add_activity(self, plan_id):
        return "", ""

    def delete_activity(self, activity_id):
        return "", ""

    def update_activity(self, activity_id):
        return "", ""
