"""Step definitions for the Recharge Plans API (health, plans, benefit review notes)."""

from behave import then, when

from lib.allure_assertions import verify_schema
from lib.schemas import ERROR_SCHEMA, PLAN_DETAIL_SCHEMA, PLAN_SUMMARY_SCHEMA


@when("I check the API health")
def step_check_health(context):
    context.response = context.client.get("/health")


@when("I request the list of all plans")
def step_list_plans(context):
    context.response = context.client.get("/plans")


@when('I request plan "{plan_id}"')
def step_get_plan(context, plan_id):
    context.response = context.client.get(f"/plans/{plan_id}")


@when('I request review notes for benefit "{benefit_id}"')
def step_get_review_notes(context, benefit_id):
    context.response = context.client.get(f"/benefits/{benefit_id}/review-notes")


@then("the response matches the plan list schema")
def step_check_plan_list_schema(context):
    verify_schema(context.response, PLAN_SUMMARY_SCHEMA)


@then("the response matches the plan detail schema")
def step_check_plan_detail_schema(context):
    verify_schema(context.response, PLAN_DETAIL_SCHEMA)


@then("the response matches the error schema")
def step_check_error_schema(context):
    verify_schema(context.response, ERROR_SCHEMA)
