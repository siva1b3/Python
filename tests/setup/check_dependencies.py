#!/usr/bin/env python3
"""Step 1: Check the dependencies installed in the development container."""

import platform
import re
import shlex
import subprocess
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path
from textwrap import indent

DOCKERFILE = Path(__file__).resolve().parents[2] / "Dockerfile"
INSTALL_PREFIX = "RUN uv pip install --python "


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    detail: str


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


def check_packages(requirements: list[str]) -> Iterator[CheckResult]:
    from packaging.requirements import Requirement

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
            yield CheckResult(
                requirement.name, False, f"Missing package: {requirement}"
            )
            continue

        expected = str(requirement.specifier) or "any installed version"
        passed = not requirement.specifier or requirement.specifier.contains(
            installed.version
        )
        yield CheckResult(
            requirement.name,
            passed,
            f"installed {installed.version}, expected {expected}",
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


def check_command(name: str, command: list[str]) -> CheckResult:
    print(f"Running {name}: {shlex.join(command)}", flush=True)
    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except OSError as error:
        return CheckResult(name, False, f"Could not start command: {error}")
    detail = f"exit code {result.returncode}"
    if result.stdout.strip():
        detail += f"\n{indent(result.stdout.strip(), '    ')}"
    return CheckResult(name, result.returncode == 0, detail)


def run_checks(dockerfile: Path) -> Iterator[CheckResult]:
    expected_python, requirements = read_expectations(dockerfile)
    print(f"Checking {len(requirements)} package requirements from {dockerfile.name}.")
    actual_python = platform.python_version()
    yield CheckResult(
        "Python version",
        actual_python == expected_python,
        f"installed {actual_python}, expected {expected_python}",
    )
    yield from check_packages(requirements)
    yield check_command("Django CLI", [sys.executable, "-m", "django", "--version"])
    yield check_command(
        "Package compatibility", ["uv", "pip", "check", "--python", sys.executable]
    )


def main(dockerfile: Path = DOCKERFILE) -> int:
    passed = failed = 0
    incomplete = False
    try:
        for result in run_checks(dockerfile):
            if result.passed:
                passed += 1
                status = "PASS"
            else:
                failed += 1
                status = "FAIL"
            print(f"[{status}] {result.name}: {result.detail}", flush=True)
    except (ImportError, OSError, ValueError) as error:
        print(f"Dependency checks stopped early: {error}", file=sys.stderr)
        incomplete = True

    total = passed + failed
    summary = f"{total} checks completed, {passed} passed, {failed} failed"
    if total:
        summary += f" ({passed / total:.1%} passed, {failed / total:.1%} failed)"
    if incomplete:
        summary += " [incomplete run]"
    print(f"Dependency check summary: {summary}.", flush=True)
    return int(failed > 0 or incomplete)


if __name__ == "__main__":
    raise SystemExit(main())
