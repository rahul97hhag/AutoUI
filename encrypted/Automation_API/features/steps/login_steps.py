"""Step definitions specific to the Login API feature.

Generic steps (setting the base URL, verifying status/JSONPath) live in
`common_steps.py` and are reused automatically by behave's step matching.
"""

from behave import when, then

from lib.allure_assertions import verify_schema

LOGIN_SUCCESS_SCHEMA = {
    "type": "object",
    "required": ["token"],
    "properties": {"token": {"type": "string", "minLength": 1}},
}


@when('I log in with email "{email}" and password "{password}"')
def step_login(context, email, password):
    context.response = context.client.post("/login", json={"email": email, "password": password})


@when('I log in with email "{email}" and no password')
def step_login_no_password(context, email):
    context.response = context.client.post("/login", json={"email": email})


@then("the response matches the login success schema")
def step_check_schema(context):
    verify_schema(context.response, LOGIN_SUCCESS_SCHEMA)
