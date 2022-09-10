import boto3


class CognitoService:
    def __init__(self, logger):
        self.cognito = boto3.client("cognito-idp")
        self.logger = logger

    def sign_up(self, clientId, body, attributes):

        response = self.cognito.sign_up(
            ClientId=clientId,
            Username=body["Email"],
            Password=body["Password"],
            UserAttributes=attributes,
        )

        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return response["UserSub"], 200
        return {"message": "Internal Server error"}, 500

    def confirm_sign_up(self, clientId, body):
        response = self.cognito.confirm_sign_up(
            ClientId=clientId,
            Username=body["Email"],
            ConfirmationCode=body["Code"],
        )

        return response["ResponseMetadata"]["HTTPStatusCode"]
