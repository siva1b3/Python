#!/usr/bin/env python3
"""Run pytest on files in the folders selected by test_config.yaml."""

import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
CONFIG_PATH = TESTS_DIR / "test_config.yaml"


def iter_test_files(parent: Path, entry: object, key: str) -> Iterator[Path]:
    if isinstance(entry, dict):
        if entry.keys() - {"path", "subfolders"}:
            raise ValueError(f"{key} supports only 'path' and 'subfolders'.")
        address = entry.get("path")
        subfolders = entry.get("subfolders", {})
    else:
        address = entry
        subfolders = {}

    if not isinstance(address, str) or not address.strip():
        raise ValueError(f"{key} needs a folder path relative to tests/.")
    if not isinstance(subfolders, dict):
        raise TypeError(f"{key}.subfolders must be a mapping.")

    relative = Path(address)
    folder = TESTS_DIR / relative
    if (
        relative.is_absolute()
        or folder.parent != parent
        or folder.resolve() != folder
        or not folder.is_dir()
    ):
        raise ValueError(
            f"{key} must point to an existing child of "
            f"{parent.relative_to(TESTS_DIR)} inside tests/."
        )

    # Passing directories to pytest would also collect unlisted subfolders.
    yield from sorted(
        file for file in folder.glob("*.py") if file.is_file() and not file.is_symlink()
    )
    for name, child in subfolders.items():
        yield from iter_test_files(folder, child, f"{key}.subfolders.{name}")


def load_config(config_path: Path) -> tuple[bool, list[Path]]:
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
    verbose = config.get("verbose", False)
    if type(verbose) is not bool:
        raise ValueError("verbose must be true or false, without quotes.")

    flags = config.get("run")
    if not isinstance(flags, dict):
        raise TypeError("Test config needs a 'run' mapping of folder flags.")
    paths = config.get("paths", {})
    if not isinstance(paths, dict):
        raise TypeError("Test config 'paths' must be a mapping.")

    files = []
    for name, enabled in flags.items():
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Invalid run flag name: {name!r}.")
        if type(enabled) is not bool:
            raise ValueError(f"run.{name} must be true or false, without quotes.")
        if enabled:
            files.extend(iter_test_files(TESTS_DIR, paths.get(name), f"paths.{name}"))
    return verbose, list(dict.fromkeys(files))


def print_tree(tree: dict, indent: str = "") -> None:
    for index, (name, children) in enumerate(sorted(tree.items())):
        last = index == len(tree) - 1
        branch = "`-- " if last else "|-- "
        suffix = "/" if children else ""
        print(f"{indent}{branch}{name}{suffix}")
        if children:
            print_tree(children, indent + ("    " if last else "|   "))


def report_skipped_files(selected: list[Path]) -> None:
    selected_files = set(selected)
    skipped = [
        file
        for file in TESTS_DIR.rglob("*.py")
        if file.parent != TESTS_DIR
        and file not in selected_files
        and file.is_file()
        and not file.is_symlink()
    ]
    print(f"Skipped Python files (excluded by YAML): {len(skipped)}")
    if not skipped:
        return

    tree = {}
    for file in skipped:
        node = tree
        for part in file.relative_to(TESTS_DIR).parts:
            node = node.setdefault(part, {})
    print("tests/")
    print_tree(tree)


def main(config_path: Path = CONFIG_PATH) -> int:
    try:
        verbose, files = load_config(config_path)
    except (OSError, TypeError, ValueError) as error:
        print(f"Test config error: {error}", file=sys.stderr)
        return 2

    report_skipped_files(files)
    if not files:
        print("No Python files selected by the test configuration.")
        return 0

    print(f"Running pytest on {len(files)} Python file(s).", flush=True)
    output_flag = "-v" if verbose else "-q"
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            output_flag,
            "--import-mode=importlib",
            *(str(file) for file in files),
        ],
        check=False,
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
