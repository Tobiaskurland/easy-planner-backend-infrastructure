import logging
import boto3


class User:
    def __init__(self, Name, Family_name, Email, Phone_number):
        self.Name = Name
        self.Family_name = Family_name
        self.Email = Email
        self.Phone_number = Phone_number


class UserService:
    def __init__(self, table, event):
        self.table = table
