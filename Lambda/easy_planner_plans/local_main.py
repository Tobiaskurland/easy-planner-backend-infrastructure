import json
import lambda_function as lf

with open('./Lambda/easy_planner_plans/events/update_plan.json', 'r') as e:
    event = json.load(e)

if __name__ == "__main__":
    response = lf.lambda_handler(event, "")
    print(response)