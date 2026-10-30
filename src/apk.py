"""Download and parse Alpine APKINDEX metadata without apk tools."""

import io
import tarfile
import urllib.error
import urllib.request


def download_index(repository_url: str, timeout: int = 20) -> str:
    """Download and decompress APKINDEX.tar.gz from a repository URL."""
    url = repository_url.rstrip("/") + "/APKINDEX.tar.gz"
    request = urllib.request.Request(
        url, headers={"User-Agent": "dependency-visualizer/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Cannot download APK index: {exc}") from exc
    try:
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
            member = archive.extractfile("APKINDEX")
            if member is None:
                raise ValueError("APKINDEX entry is missing")
            return member.read().decode("utf-8")
    except (tarfile.TarError, UnicodeDecodeError) as exc:
        raise ValueError(f"Invalid APKINDEX archive: {exc}") from exc


def parse_index(text: str) -> dict:
    """Parse APKINDEX records into package metadata dictionaries."""
    packages = {}
    record = {}
    for line in text.splitlines() + [""]:
        if not line:
            _store_record(packages, record)
            record = {}
        elif len(line) >= 2 and line[1] == ":":
            record[line[0]] = line[2:]
    return packages


def _store_record(packages: dict, record: dict) -> None:
    """Store one parsed APKINDEX record when it has a package name."""
    name = record.get("P")
    if not name:
        return
    dependencies = record.get("D", "").split()
    packages[name] = {
        "version": record.get("V", ""),
        "dependencies": dependencies,
        "provides": record.get("p", "").split(),
    }


def find_package(packages: dict, name: str, version: str) -> dict:
    """Return metadata for the exact package name and version."""
    package = packages.get(name)
    if package is None:
        raise LookupError(f"Package not found in repository: {name}")
    if package["version"] != version:
        raise LookupError(
            f"Version {version} not found for {name}; "
            f"repository has {package['version']}"
        )
    return package


def dependency_name(expression: str) -> str:
    """Extract a package token from an APK dependency expression."""
    token = expression.lstrip("!")
    for separator in ("<", ">", "=", "~"):
        token = token.split(separator, maxsplit=1)[0]
    return token.strip()
