import unittest
import boto3
from mock import patch
from plan_service import PlanService
from boto3.dynamodb.conditions import Key 


class TestPlanService(unittest.TestCase):

    def setUp(self):

        self.table = boto3.resource('dynamodb').Table('easy_planner_Staging')

    def test_get_plans_with_items(self):
    
        def mock_make_api_call(api, operation_name, kwarg):
            if operation_name == 'Query':
                self.assertEqual(Key('PK').eq('Person#unit-test') & Key('SK').begins_with('Plan'), kwarg['KeyConditionExpression'])
                return {'Items': []}
        
        with patch('botocore.client.BaseClient._make_api_call', new=mock_make_api_call):
            ps = PlanService(self.table, "unit-test")
            response, status = ps.getPlans()
            
            self.assertEqual(status, 200)
            self.assertEqual(response, [])
    
    def test_get_plans_without_items(self):
        
        def mock_make_api_call(api, operation_name, kwarg):
            if operation_name == 'Query':
                self.assertEqual(Key('PK').eq('Person#unit-test') & Key('SK').begins_with('Plan'), kwarg['KeyConditionExpression'])
                return {}
        
        with patch('botocore.client.BaseClient._make_api_call', new=mock_make_api_call):
            ps = PlanService(self.table, "unit-test")
            response, status = ps.getPlans()
            
            self.assertEqual(status, 204)
            self.assertEqual(response, {})

    def test_delete_plan(self):

        def mock_make_api_call(api, operation_name, kwarg):
            if operation_name == 'DeleteItem':

                self.assertEqual(kwarg['Key']['PK'], "Person#unit-test")
                self.assertEqual(kwarg['Key']['SK'], "Plan#mock-plan-id")

                return {'ResponseMetadata': {'HTTPStatusCode': 200}}

            if operation_name == 'GetItem':

                self.assertEqual(kwarg['Key']['PK'], "Person#unit-test")
                self.assertEqual(kwarg['Key']['SK'], "Plan#mock-plan-id")

                return {'Item': {}}
        
        with patch('botocore.client.BaseClient._make_api_call', new=mock_make_api_call):

            ps = PlanService(self.table, "unit-test")
            response, status = ps.deletePlan("mock-plan-id")

            self.assertEqual({"message": "Plan deleted successfully"}, response)
            self.assertEqual(200, status)

    def test_delete_plan_not_exist(self):

        def mock_make_api_call(api, operation_name, kwarg):

            if operation_name == 'GetItem':
                return {}
            
        with patch('botocore.client.BaseClient._make_api_call', new=mock_make_api_call):

            ps = PlanService(self.table, "unit-test")
            response, status = ps.deletePlan("mock-plan-id")

            self.assertEqual({"message": "Plan not found"}, response)
            self.assertEqual(400, status)
    
    def test_create_plan(self):

        body = {
            'StartDate': '2022-01-01',
            'EndDate': '2023-01-01',
            'Name': 'Test-name',
            'Description': 'Test-description',
            'Theme': 'Test-theme',
        }

        def mock_make_api_call(api, operation_name, kwarg):

            if operation_name == 'PutItem':

                self.assertEqual('Active', kwarg['Item']['Status'])

                return {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        with patch('botocore.client.BaseClient._make_api_call', new=mock_make_api_call):
            
            ps = PlanService(self.table, "unit-test")
            response, status = ps.createPlan(body)

            self.assertEqual({"message": "Plan created successfully"}, response)
            self.assertEqual(201, status)