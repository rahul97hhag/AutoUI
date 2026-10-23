"""Allure-reported assertion helpers for `ApiResponse` objects.

Each helper runs a check, attaches a PASS/FAIL Markdown table to the
currently open Allure step (the behave step, or the ApiClient sub-step if
called right after a request), and raises `AssertionError` with a clear
message on failure so Behave reports the step as failed.
"""

from typing import Any

import allure
from jsonpath_ng import parse as jsonpath_parse

from lib.api_client import ApiResponse

try:
    import jsonschema
except ImportError:
    jsonschema = None


def _attach_table(title: str, rows: list[dict[str, Any]]) -> None:
    """Attach a PASS/FAIL Markdown table to the current Allure step."""
    header = "| Check | Expected | Actual | Result |\n|---|---|---|---|"
    lines = [
        f"| {row['check']} | `{row['expected']}` | `{row['actual']}` | "
        f"{'✅ PASS' if row['passed'] else '❌ FAIL'} |"
        for row in rows
    ]
    allure.attach(
        "\n".join([header, *lines]),
        name=title,
        attachment_type="text/markdown",
        extension="md",
    )


def verify_status(resp: ApiResponse, expected: int) -> None:
    """Assert `resp.status_code == expected`, reporting the check to Allure."""
    passed = resp.status_code == expected
    _attach_table(
        "Verification: status code",
        [{"check": "status_code", "expected": expected, "actual": resp.status_code, "passed": passed}],
    )
    if not passed:
        raise AssertionError(f"Expected status {expected}, got {resp.status_code} ({resp.reason})")


def verify_jsonpath(resp: ApiResponse, path: str, expected: Any) -> None:
    """Assert the value(s) at JSONPath `path` in the response body equal `expected`."""
    matches = [match.value for match in jsonpath_parse(path).find(resp.json())]
    actual: Any = matches[0] if len(matches) == 1 else (matches or None)
    passed = actual == expected
    _attach_table(
        "Verification: JSONPath",
        [{"check": path, "expected": expected, "actual": actual, "passed": passed}],
    )
    if not passed:
        raise AssertionError(f"JSONPath {path!r} expected {expected!r}, got {actual!r}")


def verify_schema(resp: ApiResponse, schema: dict[str, Any]) -> None:
    """Assert the response body validates against a JSON Schema."""
    if jsonschema is None:
        raise RuntimeError("jsonschema is not installed; run: pip install jsonschema")

    errors = sorted(jsonschema.Draft7Validator(schema).iter_errors(resp.json()), key=str)
    passed = not errors
    detail = "; ".join(error.message for error in errors) if errors else "matches schema"
    _attach_table(
        "Verification: JSON schema",
        [{"check": "schema", "expected": "valid", "actual": detail, "passed": passed}],
    )
    if not passed:
        raise AssertionError(f"Schema validation failed: {detail}")
