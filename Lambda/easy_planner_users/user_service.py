import logging
import boto3
import os
import uuid
import json
import datetime
from boto3.dynamodb.conditions import Key
from dynamo_service import DynamoService
from cognito_service import CognitoService
from user_item import UserItem


class UserService:
    def __init__(self, event):
        self.event = event
        self.table = os.getenv("table")
        self.logger = logging.getLogger(__name__)
        self.ds = DynamoService(self.table)
        self.cs = CognitoService(self.logger)
        self.clientId = os.getenv("cognito_client_id")
        self.cognito = boto3.client("cognito-idp")

    def getUserById(self, user_id):

        user, status = self.ds.getUserById(user_id)
        return user.__dict__, status

    def addUser(self):

        body = json.loads(self.event["body"])
        ## ADD THE USER TO COGNITO
        cognito_response, status = self.add_user_to_cognito(body)

        ## IF THE USER COULD NOT BE CREATED IN COGNITO
        ## WE STOP AND RETURN THE STATUS
        if status != 200:
            return cognito_response, status

        ## CREATES THE USER IN DYNAMO
        user = UserItem.from_attribute_body(body, cognito_response)

        return self.ds.add_user(user.__dict__)

    def add_user_to_cognito(self, body):
        try:

            attributes = [
                {"Name": "family_name", "Value": body["FamilyName"]},
                {"Name": "name", "Value": body["FirstName"]},
                {"Name": "email", "Value": body["Email"]},
            ]

            if "PhoneNumber" in body:
                attributes.append(
                    {"Name": "phone_number", "Value": body["PhoneNumber"]}
                )

            return self.cs.sign_up(self.clientId, body, attributes)

        except self.cognito.exceptions.UsernameExistsException:
            self.logger.warn(f'[WARNING] - Username {body["Email"]} already exists')
            return {"message": "Email already registered"}, 409
        except self.cognito.exceptions.InvalidPasswordException:
            self.logger.warn(
                f"[WARNING] - Password does not meet the minimum requirements"
            )
            return {"message": "Password does not meet the minimum requirements"}, 406

    def confirm_sign_up(self):

        body = json.loads(self.event["body"])

        try:
            response = self.cs.confirm_sign_up(self.clientId, body)

            if response == 200:

                if self.verify_dynamo_user(body["Email"]) == 201:

                    return {"message": "User confirmation success"}, 200

            return {"message": "Internal Server Error"}, 500

        except self.cognito.exceptions.CodeMismatchException:
            self.logger.warn(
                f"[WARNING] - The provided confirmation code was incorrect"
            )
            return {"message": "The provided confirmation code was incorrect"}, 406
        except self.cognito.exceptions.ExpiredCodeException:
            self.logger.warn(f"[WARNING] - The confirmation code has expired")
            return {"message": "The confirmation code has expired"}, 408

    def verify_dynamo_user(self, email):

        response = self.ds.getUserByEmail(email)

        if len(response["Items"]) == 0:
            return None

        response = self.ds.verify_user(response["Items"][0])
        if response == 200:
            return 201
        return None

    def resend_confirmation_code(self):
        pass

    def updateUser(self, user_id):

        return "", 200

    def deleteUser(self, user_id):

        return "", 200
