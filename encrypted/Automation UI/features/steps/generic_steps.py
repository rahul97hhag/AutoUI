"""A small, generic step vocabulary that drives every scenario through the
config/locators.yaml registry instead of one bespoke step per page/flow.

Every interaction a browser UI test needs boils down to a handful of verbs:
navigate, click, hover, type, select, check, upload, scroll, accept a dialog,
and assert visibility/text/URL. Keeping the step text generic and pushing the
page- and field-specific detail into locators.yaml (and scenario parameters)
means new test cases are written by combining/parameterizing these steps
rather than writing new step definitions.
"""
from behave import given, when, then
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from config import locators
from utils.test_data import resolve_value


def _locate(context, page, element, value=None):
    """Resolve (page, element[, value]) to a locator, scoped to its first match.

    Templated lookups (has-text filters for product/category/brand names, cart
    rows, ...) can legitimately match more than one element on this site (e.g.
    a hover overlay duplicating its "Add to cart" link, or a search result
    whose name is a superset match of another product). Acting on/asserting
    the first match mirrors how a user would interact with the page.
    """
    return context.page.locator(locators.resolve(page, element, value)).first


@given('I navigate to the "{page}" page')
@when('I navigate to the "{page}" page')
def step_navigate(context, page):
    context.page.goto(locators.PAGE_URLS[page])


@when('I click the "{element}" on the "{page}" page')
def step_click(context, element, page):
    _locate(context, page, element).click()


@when('I click "{value}" in the "{element}" on the "{page}" page')
def step_click_dynamic(context, value, element, page):
    value = resolve_value(context, value)
    _locate(context, page, element, value).click()


@when('I hover over "{value}" in the "{element}" on the "{page}" page')
def step_hover_dynamic(context, value, element, page):
    value = resolve_value(context, value)
    _locate(context, page, element, value).hover()


@when('I enter "{value}" into the "{field}" on the "{page}" page')
def step_enter_text(context, value, field, page):
    value = resolve_value(context, value)
    _locate(context, page, field).fill(value)


@when('I select "{value}" from the "{dropdown}" on the "{page}" page')
def step_select(context, value, dropdown, page):
    _locate(context, page, dropdown).select_option(value)


@when('I check the "{checkbox}" on the "{page}" page')
def step_check(context, checkbox, page):
    _locate(context, page, checkbox).check()


@when('I upload the file "{file_path}" to the "{field}" on the "{page}" page')
def step_upload(context, file_path, field, page):
    _locate(context, page, field).set_input_files(file_path)


@when('I scroll to the "{position}" of the "{page}" page')
def step_scroll(context, position, page):
    del page  # scrolling acts on the current viewport regardless of which page it is
    if position == "bottom":
        context.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    elif position == "top":
        context.page.evaluate("window.scrollTo(0, 0)")
    else:
        raise ValueError(f"Unsupported scroll position: '{position}' (use 'top' or 'bottom')")


@when("I accept the confirmation dialog")
def step_accept_dialog(context):
    context.page.once("dialog", lambda dialog: dialog.accept())


def _assert_state(locator, state, description):
    try:
        locator.wait_for(state=state)
    except PlaywrightTimeoutError:
        raise AssertionError(f"Expected {description} to become '{state}'") from None


@then('I should see the "{element}" on the "{page}" page')
def step_should_see(context, element, page):
    _assert_state(_locate(context, page, element), "visible", f"'{element}' on the {page} page")


@then('I should see "{value}" in the "{element}" on the "{page}" page')
def step_should_see_dynamic(context, value, element, page):
    value = resolve_value(context, value)
    _assert_state(
        _locate(context, page, element, value), "visible", f"'{element}' matching '{value}' on the {page} page"
    )


@then('I should not see the "{element}" on the "{page}" page')
def step_should_not_see(context, element, page):
    _assert_state(_locate(context, page, element), "hidden", f"'{element}' on the {page} page")


@then('I should not see "{value}" in the "{element}" on the "{page}" page')
def step_should_not_see_dynamic(context, value, element, page):
    value = resolve_value(context, value)
    _assert_state(
        _locate(context, page, element, value), "hidden", f"'{element}' matching '{value}' on the {page} page"
    )


@then('the "{element}" on the "{page}" page should contain the text "{text}"')
def step_should_contain_text(context, element, page, text):
    text = resolve_value(context, text)
    actual = _locate(context, page, element).inner_text()
    assert text.lower() in actual.lower(), f"Expected '{text}' in '{actual}'"


@then('the current url should contain "{path}"')
def step_url_should_contain(context, path):
    assert path in context.page.url, f"Expected '{path}' in URL '{context.page.url}'"
