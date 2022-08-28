import logging
import boto3
import os
import uuid
import json
import datetime
from boto3.dynamodb.conditions import Key


class User:
    def __init__(
        self, Name, Family_name, Email, Phone_number, DateOfBirth, picture=None
    ):
        self.Name = Name
        self.Family_name = Family_name
        self.Email = Email
        self.Phone_number = Phone_number
        self.DateOfBirth = DateOfBirth
        self.picture = picture


class UserService:
    def __init__(self, event):
        self.event = event
        self.table = os.getenv("table")
        self.dynamodb = boto3.resource("dynamodb").Table(self.table)
        self.logger = logging.getLogger(__name__)
        self.clientId = os.getenv("cognito_client_id")
        self.cognito = boto3.client("cognito-idp")

    def getUserById(self, user_id):

        key = {"PK": f"Person#{user_id}", "SK": "INFO"}

        try:
            response = self.dynamodb.get_item(Key=key)
        except Exception as e:
            self.logger.error(
                f"[ERROR] - Unkown error when fetching user: {user_id} - {e}"
            )
            return e, 500

        if "Item" in response:
            return response["Item"], 200

        return "No Content", 204

    def addUser(self):

        body = json.loads(self.event["body"])
        cognito_response, status = self.add_user_to_cognito(body)

        if status != 200:
            return cognito_response, status

        user_item = {
            "PK": f"Person#{cognito_response}",
            "SK": "INFO",
            "Id": cognito_response,
            "DateOfBirth": body["DateOfBirth"],
            "FirstName": body["FirstName"],
            "FamilyName": body["FamilyName"],
            "Email": body["Email"],
            "GSI1_PK": body["Email"],
            "GSI1_SK": "INFO",
            "PhoneNumber": "" if "PhoneNumber" not in body else body["PhoneNumber"],
            "ProfilePicture": ""
            if "ProfilePicture" not in body
            else body["ProfilePicture"],
            "Verified": False,
        }

        try:
            response = self.dynamodb.put_item(Item=user_item)
        except Exception as e:
            self.logger.error(f"[ERROR] - Unknown error when creating user - {e}")
            return {"message": f"Internal Server Error - {e}"}, 500

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return {"message": "User created successfully"}, 201

        return {"message": "Internal Server Error"}, 500

    def add_user_to_cognito(self, body):

        attributes = [
            {"Name": "family_name", "Value": body["FamilyName"]},
            {"Name": "name", "Value": body["FirstName"]},
            {"Name": "email", "Value": body["Email"]},
        ]

        if "PhoneNumber" in body:
            attributes.append({"Name": "phone_number", "Value": body["PhoneNumber"]})

        try:
            response = self.cognito.sign_up(
                ClientId=self.clientId,
                Username=body["Email"],
                Password=body["Password"],
                UserAttributes=attributes,
            )
        except self.cognito.exceptions.UsernameExistsException:
            self.logger.warn(f'[WARNING] - Username {body["Email"]} already exists')
            return {"message": "Username already registered"}, 409
        except self.cognito.exceptions.InvalidPasswordException:
            self.logger.warn(
                f"[WARNING] - Password does not meet the minimum requirements"
            )
            return {"message": "Password does not meet the minimum requirements"}, 406
        except Exception as e:
            self.logger.error(
                f"[ERROR] - Unknown error creating user in cognito - {str(e)}"
            )
            return {"message": "Internal Server error"}, 500

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return response["UserSub"], 200

        return {"message": "Internal Server error"}, 500

    def confirm_sign_up(self):

        body = json.loads(self.event["body"])

        try:
            response = self.cognito.confirm_sign_up(
                ClientId=self.clientId,
                Username=body["Email"],
                ConfirmationCode=body["Code"],
            )
        except self.cognito.exceptions.CodeMismatchException:
            self.logger.warn(
                f"[WARNING] - The provided confirmation code was incorrect"
            )
            return {"message": "The provided confirmation code was incorrect"}, 406
        except self.cognito.exceptions.ExpiredCodeException:
            self.logger.warn(f"[WARNING] - The confirmation code has expired")
            return {"message": "The confirmation code has expired"}, 408
        except Exception as e:
            self.logger.error(
                f"[ERROR] - Failed to confirm sign up with the following error - {e}"
            )

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:

            if self.verify_dynamo_user(body["Email"]) == 201:

                return {"message": "User confirmation success"}, 200

        return {"message": "Internal Server Error"}, 500

    def verify_dynamo_user(self, email):

        key_expression = Key("GSI1_PK").eq(email) & Key("GSI1_SK").eq("INFO")

        try:
            response = self.dynamodb.query(
                KeyConditionExpression=key_expression, IndexName="GSI1"
            )
        except Exception as e:
            self.logger.error(f"[ERROR] - Failed to get user by email - {e}")

        if len(response["Items"]) == 0:

            return None

        user_item = response["Items"][0]

        try:
            response = self.dynamodb.update_item(
                Key={"PK": user_item["PK"], "SK": user_item["SK"]},
                UpdateExpression="set #Verified = :Verified",
                ExpressionAttributeNames={"#Verified": "Verified"},
                ExpressionAttributeValues={":Verified": True},
                ReturnValues="UPDATED_NEW",
            )
        except Exception as e:
            self.logger.error(
                f"[ERROR] - Failed to update dynamo user item for verification - {e}"
            )

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return 201

        return None

    def resend_confirmation_code(self):
        pass

    def updateUser(self, user_id):

        return "", 200

    def deleteUser(self, user_id):

        return "", 200
