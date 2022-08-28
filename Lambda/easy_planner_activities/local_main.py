import json
import os
import lambda_function as lf

with open("./Lambda/easy_planner_activities/events/get_activities.json", "r") as e:
    event = json.load(e)

os.environ["table"] = "easy_planner_Staging"


if __name__ == "__main__":
    response = lf.lambda_handler(event, "")
    print(response)
