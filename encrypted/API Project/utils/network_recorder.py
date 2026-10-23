"""Step-scoped network capture for Playwright pages.

NetworkRecorder.attach() registers request/response listeners once per page
(see before_scenario in features/environment.py). Behave's before_step
clears the recorded list and after_step reads it back, so each step's
Allure attachment only reflects network traffic that happened during that
specific step.

Playwright's sync API dispatches these events off the main thread, so the
listeners here only do cheap, synchronous bookkeeping -- storing headers and
object references that are already available without blocking. Anything
that can block (reading a response body) is deferred to resolve_body(),
which callers invoke from the main thread once the step has moved on.
"""
import threading

KEEP_RESOURCE_TYPES = {"xhr", "fetch", "document"}


class NetworkRecorder:
    def __init__(self):
        self._lock = threading.Lock()
        self._entries = []

    def attach(self, page):
        page.on("request", self._on_request)
        page.on("response", self._on_response)

    def _on_request(self, request):
        if request.resource_type not in KEEP_RESOURCE_TYPES:
            return
        entry = {
            "method": request.method,
            "url": request.url,
            "resource_type": request.resource_type,
            "request_headers": dict(request.headers),
            "request_post_data": request.post_data,
            "response": None,
        }
        with self._lock:
            self._entries.append(entry)

    def _on_response(self, response):
        with self._lock:
            for entry in reversed(self._entries):
                if entry["response"] is None and entry["url"] == response.url:
                    entry["response"] = {
                        "status": response.status,
                        "status_text": response.status_text,
                        "response_headers": dict(response.headers),
                        "_response": response,
                    }
                    return

    def snapshot(self):
        """The full scenario-so-far history, as a shallow copy safe to
        iterate on the main thread."""
        with self._lock:
            return list(self._entries)

    def mark(self):
        """An index into the history, taken at a step boundary. Pair with
        since() to get just the entries recorded after that point -- used
        to scope the per-step Allure attachment to that step's own traffic
        without destroying history later steps (e.g. assert_response) may
        still need to look back at."""
        with self._lock:
            return len(self._entries)

    def since(self, mark):
        with self._lock:
            return list(self._entries[mark:])


def resolve_body(response):
    """Safely read a response body. Must be called from the main thread,
    after the request/response pair has had a chance to finish -- i.e. from
    after_step or from a step definition, never from inside the
    request/response event callbacks above.

    Returns (body_text, error): error is None on success, otherwise a
    description of why the body couldn't be read.
    """
    try:
        failure = response.finished()
        if failure:
            return None, failure
    except Exception as exc:  # noqa: BLE001 - surface any Playwright error as data, not a crash
        return None, str(exc)

    try:
        return response.text(), None
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)
