#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { EasyPlannerBackendInfrastructureStack } from "../lib/easy-planner-backend-infrastructure-stack";
import { Stack, Aspects, Tag } from "aws-cdk-lib";

const app = new cdk.App();
const production = new EasyPlannerBackendInfrastructureStack(
  app,
  "EasyPlannerStackProduction",
  "PROD",
  {}
);

const staging = new EasyPlannerBackendInfrastructureStack(
  app,
  "EasyPlannerStackStaging",
  "Staging",
  {}
);

const applyTags = (stack: Stack, env: string) => {
  Aspects.of(stack).add(new Tag("Name", "Easy Planner "));
  Aspects.of(stack).add(new Tag("Project", "Easy Planner"));
  Aspects.of(stack).add(new Tag("Client", "Company"));
  Aspects.of(stack).add(new Tag("Category", "Internal Project"));
  Aspects.of(stack).add(new Tag("Country", "DK"));
};

applyTags(production, "PROD");
applyTags(staging, "STAGING");