"""Parser for the small, human-readable test repository format."""

from pathlib import Path
import re


PACKAGE_PATTERN = re.compile(r"^[A-Z]+$")


def load_test_repository(path: str) -> dict:
    """Read package edges from lines formatted as NAME:DEP1,DEP2."""
    graph = {}
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Test repository not found: {path}")
    for line_number, raw_line in enumerate(
            source.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        _parse_line(graph, line, line_number)
    if not graph:
        raise ValueError("Test repository contains no package records")
    return graph


def _parse_line(graph: dict, line: str, line_number: int) -> None:
    """Validate and store one test repository record."""
    if ":" not in line:
        raise ValueError(f"Line {line_number}: expected NAME:DEP1,DEP2")
    name, raw_dependencies = line.split(":", maxsplit=1)
    dependencies = [item.strip() for item in raw_dependencies.split(",")]
    dependencies = [item for item in dependencies if item]
    if not PACKAGE_PATTERN.fullmatch(name):
        raise ValueError(f"Line {line_number}: invalid package name {name}")
    if any(not PACKAGE_PATTERN.fullmatch(dep) for dep in dependencies):
        raise ValueError(f"Line {line_number}: invalid dependency name")
    if name in graph:
        raise ValueError(f"Line {line_number}: duplicate package {name}")
    graph[name] = dependencies
