"""Logging setup for the test run.

Two concerns, kept separate:
- `setup_logging()` wires the root logger to the console and a rotating file
  once, for the whole run.
- `AllureStreamHandler` is attached per-scenario. It buffers formatted log
  records in memory so the whole scenario's log stream can be attached to
  Allure as one readable block, instead of one attachment per log line.
"""

import logging
import logging.handlers
import os
import sys
from io import StringIO

LOG_FORMAT = "%(asctime)s.%(msecs)03d %(levelname)-7s [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(log_dir: str = "reports", log_file: str = "run.log") -> None:
    """Configure the root logger with a console handler and a rotating file handler.

    Safe to call more than once (e.g. if `before_all` runs again in-process) —
    clears any handlers from a previous call first so log lines aren't duplicated.
    """
    os.makedirs(log_dir, exist_ok=True)
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, log_file), maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)


class AllureStreamHandler(logging.Handler):
    """Buffers formatted log records in memory for later attachment to Allure.

    Usage: `start()` in `before_scenario`, `stop()` in `after_scenario` (or
    `after_step` on failure), then attach the returned text with `allure.attach`.
    """

    def __init__(self) -> None:
        super().__init__()
        self._buffer = StringIO()
        self.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    def emit(self, record: logging.LogRecord) -> None:
        self._buffer.write(self.format(record) + "\n")

    def start(self) -> None:
        """Attach this handler to the root logger."""
        logging.getLogger().addHandler(self)

    def stop(self) -> str:
        """Detach from the root logger and return everything captured so far."""
        logging.getLogger().removeHandler(self)
        return self._buffer.getvalue()

    def peek(self) -> str:
        """Return everything captured so far, without detaching."""
        return self._buffer.getvalue()
