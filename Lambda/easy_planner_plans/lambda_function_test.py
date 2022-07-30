import unittest
import json
from mock import patch
import lambda_function as lf


class TestLambdaFunction(unittest.TestCase):
    def test_get_plans(self):

        with open("./Lambda/easy_planner_plans/events/get_plans_event.json", "r") as e:
            event = json.load(e)

        def mock_make_api_call(api, operation_name, kwarg):

            if operation_name == "Query":
                return {"Items": []}

        with patch("botocore.client.BaseClient._make_api_call", new=mock_make_api_call):

            response = lf.lambda_handler(event, "")

            self.assertEqual(response["body"], "[]")
            self.assertEqual(response["statusCode"], 200)

    def test_get_plans_no_items(self):

        with open("./Lambda/easy_planner_plans/events/get_plans_event.json", "r") as e:
            event = json.load(e)

        def mock_make_api_call(api, operation_name, kwarg):

            if operation_name == "Query":
                return {}

        with patch("botocore.client.BaseClient._make_api_call", new=mock_make_api_call):

            response = lf.lambda_handler(event, "")

            self.assertEqual(response["body"], "{}")
            self.assertEqual(response["statusCode"], 204)

    def test_get_plan_by_id(self):

        with open("./Lambda/easy_planner_plans/events/get_plan_by_id.json", "r") as e:
            event = json.load(e)

        def mock_make_api_call(api, operation_name, kwarg):

            if operation_name == "Query":
                return {"Items": ["test"]}

        with patch("botocore.client.BaseClient._make_api_call", new=mock_make_api_call):

            response = lf.lambda_handler(event, "")

            self.assertEqual(response["body"], '"test"')
            self.assertEqual(response["statusCode"], 200)

    def test_get_plan_by_id_no_items(self):

        with open("./Lambda/easy_planner_plans/events/get_plan_by_id.json", "r") as e:
            event = json.load(e)

        def mock_make_api_call(api, operation_name, kwarg):

            if operation_name == "Query":
                return {}

        with patch("botocore.client.BaseClient._make_api_call", new=mock_make_api_call):

            response = lf.lambda_handler(event, "")

            self.assertEqual(response["body"], "{}")
            self.assertEqual(response["statusCode"], 204)

    def test_create_plan(self):

        with open("./Lambda/easy_planner_plans/events/create_plan.json", "r") as e:
            event = json.load(e)

        def mock_make_api_call(api, operation_name, kwarg):

            if operation_name == "PutItem":
                return {"ResponseMetadata": {"HTTPStatusCode": 200}}

        with patch("botocore.client.BaseClient._make_api_call", new=mock_make_api_call):

            response = lf.lambda_handler(event, "")

            self.assertEqual(
                response["body"], '{"message": "Plan created successfully"}'
            )
            self.assertEqual(response["statusCode"], 201)

    def test_create_plan_invalid_dates(self):

        with open("./Lambda/easy_planner_plans/events/create_plan.json", "r") as e:
            event = json.load(e)

        body = {"StartDate": "test"}

        event["body"] = json.dumps(body)

        def mock_make_api_call(api, operation_name, kwarg):

            if operation_name == "PutItem":
                return {"ResponseMetadata": {"HTTPStatusCode": 200}}

        with patch("botocore.client.BaseClient._make_api_call", new=mock_make_api_call):

            response = lf.lambda_handler(event, "")

            self.assertEqual(response["body"], '{"message": "Invalid date format"}')
            self.assertEqual(response["statusCode"], 400)

    def test_delete_plan(self):

        with open("./Lambda/easy_planner_plans/events/delete_plan.json", "r") as e:
            event = json.load(e)

        def mock_make_api_call(api, operation_name, kwarg):

            if operation_name == "GetItem":
                return {"Item": "test"}
            if operation_name == "DeleteItem":
                return {"ResponseMetadata": {"HTTPStatusCode": 200}}

        with patch("botocore.client.BaseClient._make_api_call", new=mock_make_api_call):

            response = lf.lambda_handler(event, "")

            self.assertEqual(
                response["body"], '{"message": "Plan deleted successfully"}'
            )
            self.assertEqual(response["statusCode"], 200)

    def test_update_plan(self):

        with open("./Lambda/easy_planner_plans/events/update_plan.json", "r") as e:
            event = json.load(e)

        def mock_make_api_call(api, operation_name, kwarg):

            if operation_name == "GetItem":
                return {"Item": {"Name": "", "Description": ""}}
            if operation_name == "UpdateItem":
                return {"ResponseMetadata": {"HTTPStatusCode": 200}}

        with patch("botocore.client.BaseClient._make_api_call", new=mock_make_api_call):

            response = lf.lambda_handler(event, "")

            self.assertEqual(
                response["body"], '{"message": "Plan updated successfully"}'
            )
            self.assertEqual(response["statusCode"], 201)
