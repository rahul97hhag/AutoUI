"""Generic step definitions shared by every feature.

Setting up the client and verifying status/JSONPath are the same operation
regardless of which API is under test, so they live here once instead of
being redefined per feature file.
"""

from behave import given, then

from lib.allure_assertions import verify_jsonpath, verify_status
from lib.api_client import ApiClient


@given('the API base URL is "{base_url}"')
def step_set_base_url(context, base_url):
    context.client = ApiClient(base_url)


@then("the response status should be {status:d}")
def step_check_status(context, status):
    verify_status(context.response, status)


@then('the response JSON path "{path}" should equal "{expected}"')
def step_check_jsonpath_string(context, path, expected):
    verify_jsonpath(context.response, path, expected)


@then("the response JSON path \"{path}\" should equal {expected:d}")
def step_check_jsonpath_int(context, path, expected):
    verify_jsonpath(context.response, path, expected)
