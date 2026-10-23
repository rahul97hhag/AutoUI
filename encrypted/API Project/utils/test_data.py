import random
import re
import time


_TOKEN_RE = re.compile(r"^\{\{\s*(.+?)\s*\}\}$")


def unique_suffix():
    return f"{int(time.time())}{random.randint(100, 999)}"


def random_name():
    return f"QA Tester {unique_suffix()}"


def random_email():
    return f"qa.tester.{unique_suffix()}@example.com"


def resolve_value(context, raw_value):
    """Resolve a step parameter, expanding `{{token}}` values generated/remembered per scenario.

    `{{random_name}}` / `{{random_email}}` generate a fresh value and remember it under
    `context.generated`; `{{generated.<key>}}` recalls a value generated earlier in the
    same scenario (e.g. to verify a username that was only known at signup time).
    """
    match = _TOKEN_RE.match(raw_value)
    if not match:
        return raw_value

    token = match.group(1)
    if not hasattr(context, "generated"):
        context.generated = {}

    if token == "random_name":
        context.generated["name"] = random_name()
        return context.generated["name"]
    if token == "random_email":
        context.generated["email"] = random_email()
        return context.generated["email"]
    if token.startswith("generated."):
        key = token.split(".", 1)[1]
        return context.generated[key]
    raise ValueError(f"Unknown value token: {{{{{token}}}}}")
