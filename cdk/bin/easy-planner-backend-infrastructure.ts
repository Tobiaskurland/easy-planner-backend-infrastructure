#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { EasyPlannerBackendInfrastructureStack } from "../lib/easy-planner-backend-infrastructure-stack";

const app = new cdk.App();
new EasyPlannerBackendInfrastructureStack(
  app,
  "EasyPlannerStackProduction",
  "PROD",
  {}
);

new EasyPlannerBackendInfrastructureStack(
  app,
  "EasyPlannerStackStaging",
  "Staging",
  {}
);
