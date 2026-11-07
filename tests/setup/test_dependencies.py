"""Step 1: Check the dependencies installed in the development container."""

import platform
import re
import shlex
import subprocess
import sys
from collections.abc import Iterator
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path

import pytest
from packaging.requirements import Requirement

DOCKERFILE = Path(__file__).resolve().parents[2] / "Dockerfile"
INSTALL_PREFIX = "RUN uv pip install --python "


def read_expectations(dockerfile: Path) -> tuple[str, list[str]]:
    contents = dockerfile.read_text(encoding="utf-8")
    base = re.search(r"^FROM python:(\d+\.\d+\.\d+)(?:[-\s]|$)", contents, re.MULTILINE)
    if base is None:
        raise ValueError(
            "Expected a pinned Python version in the Dockerfile's FROM line."
        )

    requirements = []
    for line in contents.replace("\\\n", " ").splitlines():
        if line.startswith(INSTALL_PREFIX):
            # Skip RUN, uv, pip, install, --python and the interpreter path.
            requirements.extend(shlex.split(line)[6:])
    if not requirements:
        raise ValueError(
            "No dependencies found in the Dockerfile's uv pip install commands."
        )
    return base.group(1), requirements


def find_package_issues(requirements: list[str]) -> Iterator[str]:
    pending = [Requirement(value) for value in reversed(requirements)]
    seen = set()
    while pending:
        requirement = pending.pop()
        if requirement in seen:
            continue
        seen.add(requirement)
        try:
            installed = distribution(requirement.name)
        except PackageNotFoundError:
            yield f"Missing package: {requirement}"
            continue

        if requirement.specifier and not requirement.specifier.contains(
            installed.version
        ):
            yield (
                f"{requirement.name}: installed {installed.version}, "
                f"expected {requirement.specifier}"
            )

        for value in installed.requires or []:
            dependency = Requirement(value)
            marker = dependency.marker
            # uv pip check covers normal dependencies. Check requested extras too.
            if (
                marker
                and not marker.evaluate({"extra": ""})
                and any(
                    marker.evaluate({"extra": extra}) for extra in requirement.extras
                )
            ):
                pending.append(dependency)


@pytest.fixture(scope="module")
def dockerfile_expectations() -> tuple[str, list[str]]:
    return read_expectations(DOCKERFILE)


def test_python_version(dockerfile_expectations: tuple[str, list[str]]) -> None:
    expected_python, _ = dockerfile_expectations
    assert platform.python_version() == expected_python


def test_installed_requirements(dockerfile_expectations: tuple[str, list[str]]) -> None:
    _, requirements = dockerfile_expectations
    issues = list(find_package_issues(requirements))
    assert not issues, "\n".join(issues)


def test_django_cli() -> None:
    subprocess.run([sys.executable, "-m", "django", "--version"], check=True)


def test_package_compatibility() -> None:
    subprocess.run(["uv", "pip", "check", "--python", sys.executable], check=True)
