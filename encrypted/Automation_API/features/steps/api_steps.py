import requests
from behave import given, when, then


@given('I want to run "{url}" api')
def step_set_api_url(context, url):
    context.api_url = url


@when('I run the api')
def step_run_api(context):
    context.api_response = requests.get(context.api_url)


@then('I print the response of the "{url}" api')
def step_print_response(context, url):
    response = context.api_response
    print(f"\nURL: {url}")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
