import json
import os
import lambda_function as lf

with open("./Lambda/easy_planner_users/events/add_user_event.json", "r") as e:
    event = json.load(e)

os.environ["table"] = "easy_planner_Staging"
os.environ["cognito_client_id"] = "7ulsc8nhv6e42h6hvd4agjumig"

if __name__ == "__main__":
    response = lf.lambda_handler(event, "")
    print(response)
