"""Writes Allure's `environment.properties` file.

Allure 2 reads this plain key=value file from the results directory and
renders it as the report's "Environment" tab. Degrades to "n/a" for any
field it can't determine (e.g. git info outside a git repo) instead of
failing the run.
"""

import os
import platform
import subprocess
from datetime import datetime


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", *args], stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:
        return "n/a"


def write_environment_properties(results_dir: str, base_url: str = "") -> None:
    """Write `environment.properties` into the Allure results directory."""
    os.makedirs(results_dir, exist_ok=True)
    properties = {
        "Base.URL": base_url or os.environ.get("BASE_URL", "n/a"),
        "Run.Timestamp": datetime.now().isoformat(timespec="seconds"),
        "Git.Branch": _git("rev-parse", "--abbrev-ref", "HEAD"),
        "Git.Commit": _git("rev-parse", "--short", "HEAD"),
        "Python.Version": platform.python_version(),
        "OS": platform.platform(),
    }
    path = os.path.join(results_dir, "environment.properties")
    with open(path, "w", encoding="utf-8") as f:
        for key, value in properties.items():
            f.write(f"{key}={value}\n")
