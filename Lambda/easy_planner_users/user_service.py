import logging

class UserService():

    def __init__(self, table):
        self.table = table

    def getUsers(self, user_id):
        
        try:
            response = self.table.get_item(Key={"PK": f"Person#{user_id}", "SK": "INFO"})
        except Exception as e:
            logging.error(f'Failed to get users - {e}')
        
        if 'Item' in response:
            return response['Item']