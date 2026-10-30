"""Loading and validating the application YAML configuration."""

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

import yaml


@dataclass(frozen=True)
class AppConfig:
    """Validated settings used by the dependency analyzer."""

    package_name: str
    repository_url: str
    test_repository: bool
    package_version: str
    filter_substring: str
    test_repository_path: str
    output_dir: str
    graph_format: str


REQUIRED_KEYS = (
    "package_name", "repository_url", "test_repository",
    "package_version", "filter_substring",
)
OPTIONAL_DEFAULTS = {
    "test_repository_path": "test_data/repository.txt",
    "output_dir": "output",
    "graph_format": "png",
}


def _read_yaml(path: Path) -> dict:
    """Read YAML and ensure its root value is a mapping."""
    if not path.is_file():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Configuration root must be a YAML mapping")
    return data


def _validate_required(data: dict) -> None:
    """Validate required keys and their value types."""
    missing = [key for key in REQUIRED_KEYS if key not in data]
    if missing:
        raise ValueError(f"Missing configuration keys: {', '.join(missing)}")
    for key in ("package_name", "repository_url", "package_version",
                "filter_substring"):
        if not isinstance(data[key], str):
            raise TypeError(f"{key} must be a string")
    if not isinstance(data["test_repository"], bool):
        raise TypeError("test_repository must be true or false")


def _validate_values(data: dict) -> None:
    """Validate package, source, version, and filter values."""
    if not data["package_name"].strip():
        raise ValueError("package_name must not be empty")
    if not data["package_version"].strip():
        raise ValueError("package_version must not be empty")
    if data["test_repository"]:
        path = Path(data["test_repository_path"])
        if not path.is_file():
            raise ValueError(f"Test repository file not found: {path}")
    else:
        parsed = urlparse(data["repository_url"])
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("repository_url must be an HTTP(S) URL")


def load_config(path: str) -> AppConfig:
    """Load, validate, and return application settings."""
    data = _read_yaml(Path(path))
    _validate_required(data)
    for key, value in OPTIONAL_DEFAULTS.items():
        data.setdefault(key, value)
    _validate_values(data)
    if data["graph_format"] not in ("png", "svg"):
        raise ValueError("graph_format must be png or svg")
    return AppConfig(**{key: data[key] for key in AppConfig.__dataclass_fields__})


def print_config(config: AppConfig) -> None:
    """Print all user-configurable settings as key-value pairs."""
    for key, value in vars(config).items():
        print(f"{key}: {value}")
