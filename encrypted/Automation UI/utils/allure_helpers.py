"""Allure attachment helpers used by features/environment.py's step hooks
and by step definitions that want to assert on captured API responses.
"""
import json
import logging

import allure
from jsonpath_ng import parse as jsonpath_parse

from utils.network_recorder import resolve_body

SENSITIVE_HEADERS = {"authorization", "cookie", "set-cookie", "x-api-key", "x-auth-token"}
REDACTED = "***"


def redact_headers(headers):
    return {key: (REDACTED if key.lower() in SENSITIVE_HEADERS else value) for key, value in headers.items()}


class ListLogHandler(logging.Handler):
    """Collects formatted log records in memory for the duration of one
    step, so that step's output can be attached to Allure without re-reading
    the shared log file."""

    def __init__(self):
        super().__init__()
        self.records = []
        self.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

    def emit(self, record):
        self.records.append(self.format(record))

    def as_text(self):
        return "\n".join(self.records) if self.records else "(no log output for this step)"


def attach_screenshot(page, name="screenshot"):
    try:
        png_bytes = page.screenshot(full_page=True)
    except Exception as exc:  # noqa: BLE001 - never let attachment capture fail the step itself
        allure.attach(str(exc), name=f"{name}-error", attachment_type=allure.attachment_type.TEXT)
        return
    allure.attach(png_bytes, name=name, attachment_type=allure.attachment_type.PNG)


def attach_logs(handler, name="step_logs"):
    allure.attach(handler.as_text(), name=name, attachment_type=allure.attachment_type.TEXT)


def _try_parse_json(raw):
    if not raw:
        return raw
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return raw


def serialize_network_entries(entries):
    """Resolve response bodies and build a JSON-safe list for the full
    per-step network trace. Reads each body at most once per entry."""
    serialized = []
    for entry in entries:
        response_meta = entry["response"]
        data = {
            "method": entry["method"],
            "url": entry["url"],
            "resource_type": entry["resource_type"],
            "request_headers": redact_headers(entry["request_headers"]),
            "request_post_data": _try_parse_json(entry["request_post_data"]),
        }
        if response_meta is None:
            data["response"] = None
        else:
            body_text, body_error = resolve_body(response_meta["_response"])
            data["response"] = {
                "status": response_meta["status"],
                "status_text": response_meta["status_text"],
                "response_headers": redact_headers(response_meta["response_headers"]),
                "body": _try_parse_json(body_text),
                "body_error": body_error,
            }
        serialized.append(data)
    return serialized


def attach_network_trace(entries, name="network_trace"):
    serialized = serialize_network_entries(entries)
    allure.attach(json.dumps(serialized, indent=2, default=str), name=name, attachment_type=allure.attachment_type.JSON)
    return serialized


def _find_main_response(entries, which):
    candidates = [e for e in entries if e["resource_type"] in ("xhr", "fetch") and e["response"] is not None]
    if which == "last_xhr":
        return candidates[-1] if candidates else None
    return next((e for e in reversed(candidates) if which in e["url"]), None)


def _attach_verification_table(rows):
    columns = ["endpoint", "exp_status", "act_status", "jsonpath", "expected", "actual", "result"]
    widths = [50, 10, 10, 22, 18, 18, 6]
    lines = ["  ".join(c.ljust(w) for c, w in zip(columns, widths))]
    lines.append("-" * sum(widths))
    for row in rows:
        lines.append("  ".join(str(v).ljust(w) for v, w in zip(row, widths)))
    if not rows:
        lines.append("(no checks were requested -- pass expected_status and/or jsonpath_checks)")
    allure.attach("\n".join(lines), name="verification_result", attachment_type=allure.attachment_type.TEXT)


def assert_response(context, expected_status=None, jsonpath_checks=None, which="last_xhr"):
    """Verify the "main" API response captured so far during the current
    step, and attach a PASS/FAIL table to Allure either way.

    context: the Behave step context (must have .network_recorder and .page,
             both set up in before_scenario/before_step).
    which:   "last_xhr" (default) picks the most recently captured XHR/fetch
             response; any other string is matched as a substring of the URL.
    """
    entries = context.network_recorder.snapshot()
    entry = _find_main_response(entries, which)

    if entry is None:
        _attach_verification_table([])
        attach_screenshot(context.page, name="assertion_failure")
        raise AssertionError("assert_response: no matching XHR/fetch response was captured during this step")

    endpoint = entry["url"]
    response_meta = entry["response"]
    body_text, body_error = resolve_body(response_meta["_response"])
    body_json = None
    if body_text is not None:
        try:
            body_json = json.loads(body_text)
        except ValueError:
            body_json = None

    rows = []
    failures = []

    if expected_status is not None:
        actual_status = response_meta["status"]
        passed = actual_status == expected_status
        rows.append((endpoint, expected_status, actual_status, "-", "-", "-", "PASS" if passed else "FAIL"))
        if not passed:
            failures.append(f"{endpoint}: expected status {expected_status}, got {actual_status}")

    for path, expected_value in (jsonpath_checks or {}).items():
        matches = jsonpath_parse(path).find(body_json) if body_json is not None else []
        actual_value = matches[0].value if matches else None
        passed = bool(matches) and actual_value == expected_value
        rows.append((endpoint, "-", "-", path, repr(expected_value), repr(actual_value), "PASS" if passed else "FAIL"))
        if not passed:
            failures.append(f"{endpoint}: {path} expected {expected_value!r}, got {actual_value!r}")

    if body_error:
        failures.append(f"{endpoint}: response body could not be read ({body_error})")

    _attach_verification_table(rows)

    if failures:
        attach_screenshot(context.page, name="assertion_failure")
        raise AssertionError("; ".join(failures))

    return {"url": endpoint, "status": response_meta["status"], "body": body_json}
