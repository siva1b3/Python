#!/usr/bin/env python3
"""Smoke test Django initialization without starting an HTTP server."""

import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"

CHECK_APPLICATION = """
import sys
from importlib import import_module

from django.apps import apps

module_name = sys.argv[1]
module = import_module(module_name)
if not apps.ready or not callable(getattr(module, "application", None)):
    raise RuntimeError(f"{module_name} did not initialize a Django application.")
"""


def main() -> int:
    checks = (
        ("Django system check", ["manage.py", "check"]),
        ("WSGI startup", ["-c", CHECK_APPLICATION, "config.wsgi"]),
        ("ASGI startup", ["-c", CHECK_APPLICATION, "config.asgi"]),
    )
    for name, args in checks:
        print(f"Checking {name}...", flush=True)
        try:
            result = subprocess.run(
                [sys.executable, *args], cwd=BACKEND_DIR, check=False, timeout=30
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            print(f"{name} failed: {error}", file=sys.stderr)
            return 1
        if result.returncode != 0:
            print(f"{name} failed (exit code {result.returncode}).", file=sys.stderr)
            return 1

    print("Django startup smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
