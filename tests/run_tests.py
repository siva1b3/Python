#!/usr/bin/env python3
"""Shared test runner configured by the adjacent test_config.yaml file."""

import subprocess
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
CONFIG_PATH = TESTS_DIR / "test_config.yaml"


def load_suites(config_path: Path) -> list[tuple[str, Path]]:
    try:
        import yaml
    except ImportError as error:
        raise ValueError(
            "PyYAML is required. Run this inside the development container."
        ) from error

    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ValueError(f"Invalid YAML in {config_path.name}: {error}") from error

    if not isinstance(config, dict):
        raise TypeError("Test config must be a YAML mapping.")
    flags, suites = config.get("run"), config.get("suites")
    if not isinstance(flags, dict) or not isinstance(suites, dict):
        raise TypeError("Test config needs 'run' and 'suites' mappings.")
    if flags.keys() != suites.keys():
        raise ValueError("Each suite must have a matching Boolean flag under 'run'.")

    enabled = []
    for name, flag in flags.items():
        if type(flag) is not bool:
            raise ValueError(f"run.{name} must be true or false, without quotes.")
        if not flag:
            continue
        suite = suites[name]
        script = suite.get("script") if isinstance(suite, dict) else None
        if not isinstance(script, str) or not script.strip():
            raise ValueError(f"suites.{name}.script must name a Python file in tests/.")
        path = (TESTS_DIR / script).resolve()
        if (
            not path.is_relative_to(TESTS_DIR)
            or path.suffix != ".py"
            or not path.is_file()
        ):
            raise ValueError(
                f"suites.{name}.script is not a Python file in tests/: {script}"
            )
        enabled.append((name, path))
    return enabled


def main(config_path: Path = CONFIG_PATH) -> int:
    try:
        enabled = load_suites(config_path)
    except (OSError, TypeError, ValueError) as error:
        print(f"Test config error: {error}", file=sys.stderr)
        return 2

    if not enabled:
        print("No test suites enabled.")
        return 0

    failed = []
    for name, script in enabled:
        print(f"Running {name}...", flush=True)
        result = subprocess.run([sys.executable, str(script)], check=False)
        if result.returncode != 0:
            failed.append(name)

    if failed:
        print(f"Failed suites: {', '.join(failed)}", file=sys.stderr)
        return 1
    print(f"Passed {len(enabled)} test suite(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
