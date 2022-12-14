import { Duration, Stack, StackProps, Tags } from "aws-cdk-lib";
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
import { RetentionDays } from "aws-cdk-lib/aws-logs";
import { Bucket, BucketEncryption } from "aws-cdk-lib/aws-s3";

function tagResource(
  scope: Construct,
  resource: String,
  stackEnvironment: string
) {
  Tags.of(scope).add("Environment", stackEnvironment);
  Tags.of(scope).add("Name", namedResource(resource));
}

function namedResource(resource: String): string {
  return "Easy Planner - " + resource;
}

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

    tagResource(dynamodbTable, "Dynamo table", env);

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
      environment: {
        table: dynamodbTable.tableName,
        cognito_client_id: "7ulsc8nhv6e42h6hvd4agjumig"
      }
    });

    tagResource(userLambda, "User Lambda", env);

    const planLambda = new Function(this, `planLambda${env}`, {
      functionName: `easy_planner_plans_${env}`,
      runtime: Runtime.PYTHON_3_9,
      code: Code.fromAsset(
        path.join(__dirname, "../../Lambda/easy_planner_plans"),
        { exclude: ["local_main.py", "events"] }
      ),
      handler: "lambda_function.lambda_handler",
      timeout: Duration.minutes(5),
      environment: {
        table: dynamodbTable.tableName
      }
    });

    tagResource(planLambda, "Plan Lambda", env);

    const activityLambda = new Function(this, `activityLambda${env}`, {
      functionName: `easy_planner_activities_${env}`,
      runtime: Runtime.PYTHON_3_9,
      code: Code.fromAsset(
        path.join(__dirname, "../../Lambda/easy_planner_activities"),
        { exclude: ["local_main.py", "events"] }
      ),
      handler: "lambda_function.lambda_handler",
      timeout: Duration.minutes(5),
      memorySize: 256,
      logRetention: RetentionDays.ONE_MONTH,
      environment: {
        table: dynamodbTable.tableName
      }
    })

    tagResource(activityLambda, "Activity Lambda", env);

    // S3

    const easyPlannerS3 = new Bucket(this, `easy_planner_s3_${env}`, {
      bucketName: `easy-planner-${env.toLowerCase()}`,
      encryption: BucketEncryption.S3_MANAGED,
      publicReadAccess: false
    })

    tagResource(easyPlannerS3, "S3 Bucket", env)

    // IAM

    const dynamodbPolicy = new PolicyStatement({
      actions: ["*"],
      resources: ["*"],
    });

    userLambda.addToRolePolicy(dynamodbPolicy);
    planLambda.addToRolePolicy(dynamodbPolicy);
    activityLambda.addToRolePolicy(dynamodbPolicy);

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

    tagResource(api, "Api Gateway", env)

    const planModel = new Model(this, `easy_planner_api_plan_model${env}`, {
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

    const userModel = new Model(this, `easy_planner_api_user_model_${env}`, {
      restApi: api,
      contentType: "application/json",
      modelName: "UserModel",
      schema: {
        schema: JsonSchemaVersion.DRAFT4,
        title: "CreateUserModel",
        type: JsonSchemaType.OBJECT,
        required: ["FirstName", "FamilyName", "Email", "DateOfBirth", "Password"],
        properties: {
          FirstName: { type: JsonSchemaType.STRING },
          FamilyName: { type: JsonSchemaType.STRING },
          Email: { type: JsonSchemaType.STRING },
          DateOfBirth: { type: JsonSchemaType.STRING },
          Password: { type: JsonSchemaType.STRING },
        },
      },
    });

    const activityModel = new Model(this, `easy_planner_api_activity_model_${env}`, {
      restApi: api,
      contentType: "application/json",
      modelName: "ActivityModel",
      schema: {
        schema: JsonSchemaVersion.DRAFT4,
        title: "createActivityModel",
        type: JsonSchemaType.OBJECT,
        required: ["Date", "Description", "StartTime", "EndTime", "Name", "Theme"],
        properties:
        {
          Date: { type: JsonSchemaType.STRING},
          Description: { type: JsonSchemaType.STRING },
          StartTime: {type: JsonSchemaType.STRING},
          EndTime: {type: JsonSchemaType.STRING},
          Name: {type: JsonSchemaType.STRING},
          Theme: { type: JsonSchemaType.STRING },
        }
      }
    })

    const requestValidator = new RequestValidator(
      this,
      `easy_planner_api_request_validator${env}`,
      {
        restApi: api,
        requestValidatorName: "requestValidator",
        validateRequestBody: true,
      }
    );

    const userLambdaIntegration = new LambdaIntegration(userLambda);
    const planLambdaIntegration = new LambdaIntegration(planLambda);
    const activityLambdaIntegration = new LambdaIntegration(activityLambda);

    const user = api.root.addResource("user");
    user.addMethod("GET", userLambdaIntegration, {
      authorizer: auth,
      authorizationType: AuthorizationType.COGNITO,
    });
    user.addMethod("POST", userLambdaIntegration, {
      requestValidator: requestValidator,
      requestModels: {"application/json": userModel}
    });
    user.addMethod("DELETE", userLambdaIntegration, {
      authorizer: auth,
      authorizationType: AuthorizationType.COGNITO,
    });
    user.addMethod("PUT", userLambdaIntegration, {
      authorizer: auth,
      authorizationType: AuthorizationType.COGNITO
    });

    const confirm_user = user.addResource("confirm");
    confirm_user.addMethod("POST", userLambdaIntegration);
    confirm_user.addMethod("GET", userLambdaIntegration);

    const plans = api.root.addResource("plans");
    plans.addMethod("GET", planLambdaIntegration, {
      authorizer: auth,
      authorizationType: AuthorizationType.COGNITO,
    });
    plans.addMethod("POST", planLambdaIntegration, {
      authorizer: auth,
      authorizationType: AuthorizationType.COGNITO,
      requestValidator: requestValidator,
      requestModels: { "application/json": planModel },
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
    const plan_activities = plan.addResource("activities")
    plan_activities.addMethod("GET", activityLambdaIntegration, {
      authorizer: auth,
      authorizationType: AuthorizationType.COGNITO
    });
    plan_activities.addMethod("POST", activityLambdaIntegration, {
      authorizer: auth,
      authorizationType: AuthorizationType.COGNITO,
      requestValidator: requestValidator,
      requestModels: {"application/json": activityModel}
    });

    const activities = api.root.addResource("activities");
    const activity = activities.addResource("{activity_id}");
    activity.addMethod("GET", activityLambdaIntegration, {
      authorizer: auth,
      authorizationType: AuthorizationType.COGNITO
    });
    activity.addMethod("DELETE", activityLambdaIntegration, {
      authorizer: auth,
      authorizationType: AuthorizationType.COGNITO
    });
    activity.addMethod("PUT", activityLambdaIntegration, {
      authorizer: auth,
      authorizationType: AuthorizationType.COGNITO
    });
  }
}
