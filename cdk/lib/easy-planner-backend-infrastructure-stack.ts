import { Duration, Stack, StackProps } from "aws-cdk-lib";
import { AttributeType, BillingMode, Table } from "aws-cdk-lib/aws-dynamodb";
import {
  AuthorizationType,
  CognitoUserPoolsAuthorizer,
  Cors,
  JsonSchemaType,
  JsonSchemaVersion,
  LambdaIntegration,
  LambdaRestApi,
  Model,
  RequestValidator,
} from "aws-cdk-lib/aws-apigateway";
import { Construct } from "constructs";
import { Code, Function, Runtime } from "aws-cdk-lib/aws-lambda";
import * as path from "path";
import { UserPool } from "aws-cdk-lib/aws-cognito";
import { PolicyStatement } from "aws-cdk-lib/aws-iam";

export class EasyPlannerBackendInfrastructureStack extends Stack {
  constructor(scope: Construct, id: string, env: string, props?: StackProps) {
    super(scope, id, props);

    // DYNAMODB
    const dynamodbTable = new Table(this, `easyPlannerDynamoDB${env}`, {
      tableName: `easy_planner_${env}`,
      partitionKey: { name: "PK", type: AttributeType.STRING },
      sortKey: { name: "SK", type: AttributeType.STRING },
      billingMode: BillingMode.PAY_PER_REQUEST,
    });

    dynamodbTable.addGlobalSecondaryIndex({
      indexName: "GSI1",
      partitionKey: { name: "GSI1_PK", type: AttributeType.STRING },
      sortKey: { name: "GSI1_SK", type: AttributeType.STRING },
    });

    // COGNITO

    const cognito = UserPool.fromUserPoolId(
      this,
      `easyPlannerCognito${env}`,
      "eu-west-1_p0D65QE05"
    );

    // LAMBDA

    const userLambda = new Function(this, `userLambda${env}`, {
      functionName: `easy_planner_users_${env}`,
      runtime: Runtime.PYTHON_3_9,
      code: Code.fromAsset(
        path.join(__dirname, "../../Lambda/easy_planner_users"),
        { exclude: ["local_main.py", "events"] }
      ),
      handler: "lambda_function.lambda_handler",
      timeout: Duration.minutes(5),
    });

    const planLambda = new Function(this, `planLambda${env}`, {
      functionName: `easy_planner_plans_${env}`,
      runtime: Runtime.PYTHON_3_9,
      code: Code.fromAsset(
        path.join(__dirname, "../../Lambda/easy_planner_plans"),
        { exclude: ["local_main.py", "events"] }
      ),
      handler: "lambda_function.lambda_handler",
      timeout: Duration.minutes(5),
    });

    // IAM

    const dynamodbPolicy = new PolicyStatement({
      actions: ["*"],
      resources: ["*"],
    });

    userLambda.addToRolePolicy(dynamodbPolicy);
    planLambda.addToRolePolicy(dynamodbPolicy);

    // API GATEWAY

    const auth = new CognitoUserPoolsAuthorizer(
      this,
      `easyPlannerAuthorizer${env}`,
      {
        cognitoUserPools: [cognito],
      }
    );

    const api = new LambdaRestApi(this, `easy_planner_api_${env}`, {
      handler: userLambda,
      proxy: false,
      defaultCorsPreflightOptions: {
        allowOrigins: Cors.ALL_ORIGINS,
        allowMethods: Cors.ALL_METHODS,
      },
    });

    const model = new Model(this, `easy_planner_api_plan_model${env}`, {
      restApi: api,
      contentType: "application/json",
      modelName: "PlanModel",
      schema: {
        schema: JsonSchemaVersion.DRAFT4,
        title: "createPlanModel",
        type: JsonSchemaType.OBJECT,
        required: ["Name", "Description", "StartDate", "EndDate", "Theme"],
        properties: {
          Name: { type: JsonSchemaType.STRING },
          Description: { type: JsonSchemaType.STRING },
          StartDate: { type: JsonSchemaType.STRING },
          EndDate: { type: JsonSchemaType.STRING },
          Theme: { type: JsonSchemaType.STRING },
        },
      },
    });

    const requestValidator = new RequestValidator(
      this,
      `easy_planner_api_request_validator${env}`,
      {
        restApi: api,
        requestValidatorName: "PlanRequestValidator",
        validateRequestBody: true,
      }
    );

    const userLambdaIntegration = new LambdaIntegration(userLambda);
    const planLambdaIntegration = new LambdaIntegration(planLambda);

    const users = api.root.addResource("user");
    users.addMethod("POST", userLambdaIntegration, {
      authorizer: auth,
      authorizationType: AuthorizationType.COGNITO,
    });

    const user = users.addResource("{user_id}");
    user.addMethod("GET", userLambdaIntegration, {
      authorizer: auth,
      authorizationType: AuthorizationType.COGNITO,
    });
    user.addMethod("DELETE", userLambdaIntegration, {
      authorizer: auth,
      authorizationType: AuthorizationType.COGNITO,
    });

    const plans = api.root.addResource("plans");
    plans.addMethod("GET", planLambdaIntegration, {
      authorizer: auth,
      authorizationType: AuthorizationType.COGNITO,
    });
    plans.addMethod("POST", planLambdaIntegration, {
      authorizer: auth,
      authorizationType: AuthorizationType.COGNITO,
      requestValidator: requestValidator,
      requestModels: { "application/json": model },
    });

    const plan = plans.addResource("{plan_id}");
    plan.addMethod("GET", planLambdaIntegration, {
      authorizer: auth,
      authorizationType: AuthorizationType.COGNITO,
    });
    plan.addMethod("DELETE", planLambdaIntegration, {
      authorizer: auth,
      authorizationType: AuthorizationType.COGNITO,
    });
    plan.addMethod("PUT", planLambdaIntegration, {
      authorizer: auth,
      authorizationType: AuthorizationType.COGNITO,
    });
  }
}
