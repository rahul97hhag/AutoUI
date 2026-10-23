import logging
import sys
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent.parent / "reports" / "run.log"

_root = logging.getLogger("file_vault_ui")
_root.setLevel(logging.INFO)
_root.propagate = False

if not _root.handlers:
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    _root.addHandler(stream_handler)

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    _root.addHandler(file_handler)


def get_logger(name):
    return _root.getChild(name)


def get_root_logger():
    """The shared root logger, for code (e.g. a step-scoped log handler)
    that needs to attach/detach handlers rather than just emit records."""
    return _root
