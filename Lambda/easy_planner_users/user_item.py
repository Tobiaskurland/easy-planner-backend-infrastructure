class UserItem:
    def __init__(self) -> None:
        self.Verified = False

    def _load_from_dynamo_item(self, item):
        self.PK = item.get("PK", None)
        self.Id = item.get("Id", None)
        self.FirstName = item.get("FirstName", None)
        self.FamilyName = item.get("FamilyName", None)
        self.Email = item.get("Email", None)
        self.DateOfBirth = item.get("DateOfBirth", None)
        self.GSI1_PK = item.get("GSI1_PK", None)
        self.SK = item.get("SK", None)
        self.GSI1_SK = item.get("GSI1_SK", None)
        self.PhoneNumber = item.get("PhoneNumber", None)
        self.ProfilePicture = item.get("ProfilePicture", None)
        self.Verified = item.get("Verified", None)

    def _load_from_attribute_body(self, body, id):
        self.PK = f"Person#{id}"
        self.Id = id
        self.FirstName = body["FirstName"]
        self.FamilyName = body["FamilyName"]
        self.Email = body["Email"]
        self.DateOfBirth = body["DateOfBirth"]
        self.GSI1_PK = body["Email"]
        self.SK = "INFO"
        self.GSI1_SK = "INFO"

    def _attach_phone_number(self, phone_number):
        self.PhoneNumber = phone_number

    def _attach_profile_picture(self, profile_picture):
        self.ProfilePicture = profile_picture

    @staticmethod
    def from_attribute_body(body, id):
        userItem = UserItem()
        userItem._load_from_attribute_body(body, id)

        if "PhoneNumber" in body:
            userItem._attach_phone_number(body["PhoneNumber"])
        if "ProfilePicture" in body:
            userItem._attach_profile_picture(body["ProfilePicture"])
        return userItem

    @staticmethod
    def from_dynamo_item(item):
        userItem = UserItem()
        userItem._load_from_dynamo_item(item)
        return userItem
