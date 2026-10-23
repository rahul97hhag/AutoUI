"""Requests-based HTTP client that auto-reports every call to Allure.

Every call to `ApiClient.request()` (and its verb shortcuts) opens a nested
Allure step named "METHOD /path" and attaches `request.json`, `response.json`
and `api_trace.txt` to it, so evidence always lands under the correct node in
the report tree without any Allure code in step files.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
from urllib.parse import urlsplit

import allure
import requests

logger = logging.getLogger("api_client")

# kwargs that belong on the Request itself vs. ones that only apply at send time.
_REQUEST_KWARGS = {"params", "data", "json", "headers", "cookies", "files", "auth"}
_SEND_KWARGS = {"timeout", "allow_redirects", "proxies", "stream", "verify", "cert"}


@dataclass
class ApiResponse:
    """Normalized result of an API call."""

    status_code: int
    reason: str
    headers: dict[str, str]
    text: str
    elapsed_ms: float
    raw_request: requests.PreparedRequest
    raw_response: requests.Response

    def json(self) -> Any:
        """Parse the response body as JSON."""
        return self.raw_response.json()


def _pretty_body(raw: Optional[bytes | str], content_type: str) -> str:
    """Pretty-print a request/response body as JSON when possible, else return as-is."""
    if raw is None:
        return ""
    text = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else raw
    if not text:
        return ""
    if "json" in (content_type or "") or text.strip().startswith(("{", "[")):
        try:
            return json.dumps(json.loads(text), indent=2, sort_keys=True)
        except (json.JSONDecodeError, TypeError):
            return text
    return text


def _curl_equivalent(request: requests.PreparedRequest) -> str:
    """Build a copy-pasteable curl command for the given prepared request."""
    parts = [f"curl -X {request.method}", f"'{request.url}'"]
    for key, value in request.headers.items():
        parts.append(f"-H '{key}: {value}'")
    if request.body:
        body = (
            request.body.decode("utf-8", errors="replace")
            if isinstance(request.body, bytes)
            else request.body
        )
        parts.append(f"-d '{body}'")
    return " ".join(parts)


class ApiClient:
    """Thin `requests.Session` wrapper that reports every call to Allure."""

    def __init__(self, base_url: str = "", default_headers: Optional[dict[str, str]] = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        if default_headers:
            self.session.headers.update(default_headers)

    def request(self, method: str, url: str, **kwargs: Any) -> ApiResponse:
        """Perform an HTTP call, reporting request/response evidence to Allure.

        Args:
            method: HTTP verb, e.g. "GET", "POST".
            url: Absolute URL, or a path appended to `base_url`. Path params
                should already be substituted into the URL by the caller.
            **kwargs: Forwarded to `requests`, e.g. `json=`, `params=`,
                `headers=`, `timeout=`.

        Returns:
            ApiResponse wrapping the result.
        """
        full_url = url if url.startswith("http") else f"{self.base_url}/{url.lstrip('/')}"
        endpoint_path = urlsplit(full_url).path
        step_name = f"{method.upper()} {endpoint_path}"

        request_kwargs = {k: v for k, v in kwargs.items() if k in _REQUEST_KWARGS}
        send_kwargs = {k: v for k, v in kwargs.items() if k in _SEND_KWARGS}

        with allure.step(step_name):
            prepared = self.session.prepare_request(
                requests.Request(method=method.upper(), url=full_url, **request_kwargs)
            )

            started_at = datetime.now()
            logger.info("[%s] Sending %s %s", started_at.isoformat(timespec="milliseconds"), prepared.method, prepared.url)

            response = self.session.send(prepared, **send_kwargs)

            finished_at = datetime.now()
            elapsed_ms = response.elapsed.total_seconds() * 1000
            logger.info(
                "[%s] Received %s %s in %.1fms",
                finished_at.isoformat(timespec="milliseconds"),
                response.status_code,
                response.reason,
                elapsed_ms,
            )

            api_response = ApiResponse(
                status_code=response.status_code,
                reason=response.reason,
                headers=dict(response.headers),
                text=response.text,
                elapsed_ms=elapsed_ms,
                raw_request=prepared,
                raw_response=response,
            )

            self._attach_evidence(prepared, api_response, request_kwargs, started_at, finished_at)
            return api_response

    def get(self, url: str, **kwargs: Any) -> ApiResponse:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> ApiResponse:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> ApiResponse:
        return self.request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> ApiResponse:
        return self.request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> ApiResponse:
        return self.request("DELETE", url, **kwargs)

    @staticmethod
    def _attach_evidence(
        prepared: requests.PreparedRequest,
        resp: ApiResponse,
        request_kwargs: dict[str, Any],
        started_at: datetime,
        finished_at: datetime,
    ) -> None:
        """Attach request.json, response.json and api_trace.txt to the current Allure step."""
        request_payload = {
            "method": prepared.method,
            "url": prepared.url,
            "query_params": request_kwargs.get("params"),
            "headers": dict(prepared.headers),
            "body": _pretty_body(prepared.body, prepared.headers.get("Content-Type", "")),
        }
        allure.attach(
            json.dumps(request_payload, indent=2, default=str),
            name="request.json",
            attachment_type=allure.attachment_type.JSON,
        )

        response_payload = {
            "status_code": resp.status_code,
            "reason": resp.reason,
            "elapsed_ms": round(resp.elapsed_ms, 1),
            "headers": resp.headers,
            "body": _pretty_body(resp.text, resp.headers.get("Content-Type", "")),
        }
        allure.attach(
            json.dumps(response_payload, indent=2, default=str),
            name="response.json",
            attachment_type=allure.attachment_type.JSON,
        )

        trace_lines = [
            f"# {prepared.method} {prepared.url}",
            "",
            f"Started  : {started_at.isoformat(timespec='milliseconds')}",
            f"Finished : {finished_at.isoformat(timespec='milliseconds')}",
            "",
            "## curl",
            _curl_equivalent(prepared),
            "",
            "## Response",
            f"Status : {resp.status_code} {resp.reason}",
            f"Time   : {resp.elapsed_ms:.1f}ms",
            "",
            "## Response body",
            _pretty_body(resp.text, resp.headers.get("Content-Type", "")),
        ]
        allure.attach(
            "\n".join(trace_lines),
            name="api_trace.txt",
            attachment_type=allure.attachment_type.TEXT,
        )
