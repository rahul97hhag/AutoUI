You are a senior Python test automation architect. I have an existing API automation framework 
built with Python + Behave + Requests, producing HTML and Allure reports.

Currently it only runs endpoints and shows pass/fail in reports. That is not enough.

## GOAL
Upgrade the framework so that every Behave step attaches rich, human-readable evidence 
to the Allure report, and also produces a clean HTML summary.

For EACH API call performed inside a step, the Allure report must show:
1. Step-level logs (what happened, in order, timestamped).
2. Request details:
   - Method + full URL + endpoint
   - Request headers
   - Request body (pretty-printed JSON if applicable)
   - Query params / path params (if any)
3. Response details:
   - Status code
   - Status message / reason
   - Response headers
   - Response content/body (pretty-printed JSON if applicable)
   - Response time (ms)
4. Verification section:
   - Status code comparison (expected vs actual, PASS/FAIL)
   - JSONPath assertions with expected vs actual values, PASS/FAIL, and the JSON path used
   - Any schema validation result (if applicable)
5. Attachments in Allure:
   - request.json
   - response.json
   - a combined `api_trace.txt` (curl-equivalent + response + assertions)

## CONSTRAINTS
- Keep it simple and maintainable. No over-engineering.
- Allure integration must use `allure.step`, `allure.attach`, and `allure.dynamic.*` correctly.
- Use `requests` + a wrapper layer (e.g., `ApiClient`) that automatically captures everything.
- Attachments must appear under the CORRECT step in the Allure tree — not at the end of the test.
- Behave `environment.py` hooks should attach on failure (screenshot-equivalent = full trace).
- Logging must also go to a Python `logging` logger AND to Allure.
- Must be reusable: any new endpoint gets this reporting for free, without extra code in step files.

## DELIVERABLES — do them in this exact order, one step at a time

**Step 1:** Design overview.
Explain the architecture: how ApiClient, a reporting helper, behave hooks, and allure steps 
fit together. Include a folder/file layout. WAIT for my "continue" before proceeding.

**Step 2:** Implement `api_client.py`.
A `requests.Session`-based wrapper with a single public method `request(method, url, **kwargs)` 
that:
- captures request/response,
- emits a nested `allure.step` named like "POST /users",
- attaches request.json, response.json, api_trace.txt inside that step,
- returns a custom `ApiResponse` dataclass with `.status_code`, `.json()`, `.headers`, 
  `.elapsed_ms`, `.text`, `.raw_request`, `.raw_response`.
Show complete code. WAIT for my "continue".

**Step 3:** Implement `allure_assertions.py`.
Helpers like `verify_status(resp, expected)`, `verify_jsonpath(resp, path, expected)` 
that:
- run the check,
- build a small table (Markdown) of PASS/FAIL, expected, actual, path,
- `allure.attach` it as `text/markdown` to the current step,
- raise AssertionError on failure with a clear message.
Show complete code. WAIT for my "continue".

**Step 4:** Implement Behave integration.
- `environment.py` (before_all, before_scenario, before_step, after_step, after_scenario, after_all).
- How to ensure the trace attaches under the failing step.
- Logging configuration (console + file + Allure stream handler).
Show complete code. WAIT for my "continue".

**Step 5:** Example feature + step file.
Show a realistic `login.feature` and `steps/login_steps.py` that use the ApiClient + 
assertions, demonstrating that reports show everything described above. WAIT for my "continue".

**Step 6:** Allure config + run commands.
- `allure.properties`, `pytest`/`behave` CLI flags, `environment.xml` population 
  (commit, branch, env, base_url, run timestamp).
- How to generate and open the report.
- Explain what the final Allure tree will look like (textual mockup). WAIT for my "continue".

**Step 7:** Validation checklist.
A bullet list I can tick off in the Allure UI to confirm every requirement is met 
(request headers, body, status, verification table, JSONPath results, etc.). 
Also list common pitfalls (e.g., attachments in `after_step` appearing in wrong place) 
and how your design avoids them.

## RULES
- Do NOT proceed to the next step until I say "continue".
- At the end of each step, end with: "✅ Step N complete. Say **continue** for Step N+1."
- Use type hints, docstrings, and modern Python (3.10+).
- Assume Allure is already installed (`allure-pytest` is NOT enough — we use `allure-behave` 
  or the `allure` package directly). If a package choice matters, explain it in Step 1.
- If something in my current setup could conflict, call it out in Step 1.

