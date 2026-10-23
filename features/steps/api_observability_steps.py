"""Step definitions demonstrating assert_response() (utils/allure_helpers.py)
against a response the running page genuinely receives.

automationexercise.com's own UI is server-rendered -- its pages don't fire
XHR/fetch calls on their own -- but the site also publishes a small REST API
for practice at /api_list (e.g. GET /api/productsList ->
{"responseCode": 200, "products": [...]}). Calling it via page.evaluate()'s
fetch() makes it a real request/response the current page's
NetworkRecorder observes the same way it would observe any API call the
site's own JS made, so this exercises the full Phase 1-3 pipeline
end-to-end rather than mocking it.
"""
import json

from behave import when, then

from utils.allure_helpers import assert_response


@when('I call the GET API "{path}" from the page')
def step_call_api(context, path):
    url = path if path.startswith("http") else f"{context.config_data['base_url']}{path}"
    context.page.evaluate(f"() => fetch('{url}')")


@then("the API response should have status {expected_status:d}")
def step_check_status_only(context, expected_status):
    assert_response(context, expected_status=expected_status)


@then('the API response field "{json_path}" should equal {expected_value}')
def step_check_jsonpath(context, json_path, expected_value):
    try:
        expected = json.loads(expected_value)
    except ValueError:
        expected = expected_value
    assert_response(context, jsonpath_checks={json_path: expected})
