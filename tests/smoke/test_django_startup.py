"""Smoke test Django initialization without starting an HTTP server."""

import subprocess
import sys
from pathlib import Path

import pytest

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


def test_django_system_check() -> None:
    subprocess.run(
        [sys.executable, "manage.py", "check"],
        cwd=BACKEND_DIR,
        check=True,
        timeout=30,
    )


@pytest.mark.parametrize("interface", ["wsgi", "asgi"])
def test_application_initializes(interface: str) -> None:
    subprocess.run(
        [sys.executable, "-c", CHECK_APPLICATION, f"config.{interface}"],
        cwd=BACKEND_DIR,
        check=True,
        timeout=30,
    )
