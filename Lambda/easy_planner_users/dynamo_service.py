import boto3
from boto3.dynamodb.conditions import Key


class DynamoService:
    def __init__(self, table):
        self.table = boto3.resource("dynamodb").Table(table)

    def getUserById(self, id):
        response = self.table.get_item(Key={"PK": f"Person#{id}", "SK": "INFO"})
        if "Item" not in response:
            return "No Content", 204
        return response["Item"], 200

    def getUserByEmail(self, email):
        key_expression = Key("GSI1_PK").eq(email) & Key("GSI1_SK").eq("INFO")
        return self.table.query(KeyConditionExpression=key_expression, IndexName="GSI1")

    def add_user(self, user):
        response = self.table.put_item(Item=user)
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return {"message": "User created successfully"}, 201

        return {"message": "Internal Server Error"}, 500

    def verify_user(self, user_item):
        response = self.table.update_item(
            Key={"PK": user_item["PK"], "SK": user_item["SK"]},
            UpdateExpression="set #Verified = :Verified",
            ExpressionAttributeNames={"#Verified": "Verified"},
            ExpressionAttributeValues={":Verified": True},
            ReturnValues="UPDATED_NEW",
        )

        return response["ResponseMetadata"]["HTTPStatusCode"]
