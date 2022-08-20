import logging
import boto3
import os


class ActivityService:
    def __init__(self, user_id):
        self.user_id = user_id
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.debug)
        self.table = os.getenv("table")
        self.dynamodb = boto3.resource("dynamodb").Table(self.table)

    def get_user_activities(self):
        return "", ""

    def get_user_activity_by_id(self, activity_id):
        return "", ""

    def add_activity(self):
        return "", ""

    def delete_activity(self, activity_id):
        return "", ""

    def update_activity(self, activity_id):
        return "", ""
