import logging
import uuid
from datetime import datetime
from boto3.dynamodb.conditions import Key


class PlanService:
    def __init__(self, table, user_id):
        self.table = table
        self.user_id = user_id

    def getPlans(self):

        key_expression = Key("PK").eq(f"Person#{self.user_id}") & Key("SK").begins_with(
            "Plan"
        )

        try:
            response = self.table.query(KeyConditionExpression=key_expression)
        except Exception as e:
            logging.error(f"Failed to get plans - {e}")

        if "Items" in response:
            return response["Items"], 200
        else:
            return {}, 204

    def getPlanById(self, plan_id):

        key_expression = Key("PK").eq(f"Person#{self.user_id}") & Key("SK").eq(
            f"Plan#{plan_id}"
        )

        try:
            response = self.table.query(KeyConditionExpression=key_expression)
        except Exception as e:
            logging.error(f"Failed to get plan - {e}")

        if "Items" in response:
            return response["Items"][0], 200
        else:
            return {}, 204

    def deletePlan(self, plan_id):

        key = {"PK": f"Person#{self.user_id}", "SK": f"Plan#{plan_id}"}

        try:
            planItem = self.table.get_item(Key=key)
        except Exception as e:
            logging.warning(f"Failed to get plan - {e}")

        if "Item" not in planItem:
            return {"message": "Plan not found"}, 400

        try:
            response = self.table.delete_item(Key=key)
        except Exception as e:
            logging.error(f"Failed to delete plan - {e}")

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return {"message": "Plan deleted successfully"}, 200
        else:
            return {"message": "Internal Server Error"}, 500

    def createPlan(self, body):

        id = uuid.uuid4().hex
        pk = f"Person#{self.user_id}"
        sk = f"Plan#{id}"

        dateFormat = "%Y-%m-%d"

        try:
            startDate = datetime.strptime(body["StartDate"], dateFormat)
            endDate = datetime.strptime(body["EndDate"], dateFormat)
        except ValueError as e:
            logging.warning(f"Invalid date format - {e}")
            return {"message": "Invalid date format"}, 400
        except Exception as e:
            logging.error(f"Failed to convert dates - {e}")

        dateToday = datetime.now()

        plan_status = "Inactive"
        if startDate <= dateToday <= endDate:
            plan_status = "Active"

        try:
            response = self.table.put_item(
                Item={
                    "PK": pk,
                    "SK": sk,
                    "Id": id,
                    "StartDate": body["StartDate"],
                    "EndDate": body["EndDate"],
                    "Name": body["Name"],
                    "Description": body["Description"],
                    "Theme": body["Theme"],
                    "Status": plan_status,
                }
            )
        except Exception as e:
            logging.error(f"Failed to create plan - {e}")

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return {"message": "Plan created successfully"}, 201
        else:
            return {"message": "Internal Server Error"}, 500

    def updatePlan(self, plan_id, body):

        item_key = {"PK": f"Person#{self.user_id}", "SK": f"Plan#{plan_id}"}
        invalid_attribute = self.get_invalid_attribute(item_key, body)

        if invalid_attribute is None:

            (
                update_expression,
                attributeNames,
                attributeValues,
            ) = self.get_update_expressions(body)

            try:
                response = self.table.update_item(
                    Key=item_key,
                    UpdateExpression=update_expression,
                    ExpressionAttributeNames=attributeNames,
                    ExpressionAttributeValues=attributeValues,
                    ReturnValues="UPDATED_NEW",
                )

            except Exception as e:
                logging.error(f"Failed to update item - {e}")

            if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
                return {"message": "Plan updated successfully"}, 201
            else:
                return {"message": "Internal Server Error"}, 500

        else:
            return {
                "message": f"No attribute matching {invalid_attribute} found in plan item"
            }, 400

    def get_invalid_attribute(self, item_key, body):

        try:
            planItem = self.table.get_item(Key=item_key)
        except Exception as e:
            logging.warning(f"Failed to get plan - {e}")

        if "Item" not in planItem:
            return {"message": "Plan not found"}, 400
        else:
            for itemKey in body.keys():
                if itemKey not in planItem["Item"]:
                    return itemKey
            return None

    def get_update_expressions(self, body):

        attributeNames = {}
        attributeValues = {}

        for key in body.keys():
            attributeNames[f"#{key}"] = key

        for key, value in body.items():
            attributeValues[f":{key}"] = value

        update_expression = "set "
        separator = ""

        for value in attributeNames.values():
            update_expression = f"{update_expression}{separator}#{value} = :{value}"
            separator = ", "

        return update_expression, attributeNames, attributeValues
