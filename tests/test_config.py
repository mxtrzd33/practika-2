"""Tests for YAML configuration validation."""

import tempfile
import unittest
from pathlib import Path

from src.config import load_config


VALID = """\
package_name: A
repository_url: ""
test_repository: true
package_version: "1"
filter_substring: ""
test_repository_path: "{repo}"
"""


class ConfigTests(unittest.TestCase):
    """Cover valid configuration and common validation errors."""

    def test_load_valid_config(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder) / "repo.txt"
            repo.write_text("A:\\n", encoding="utf-8")
            config = Path(folder) / "config.yaml"
            config.write_text(VALID.format(repo=repo), encoding="utf-8")
            self.assertEqual(load_config(str(config)).package_name, "A")

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_config("missing-config.yaml")

    def test_missing_key(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.yaml"
            path.write_text("package_name: A\\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config(str(path))

    def test_wrong_mode_type(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder) / "repo.txt"
            repo.write_text("A:\\n", encoding="utf-8")
            path = Path(folder) / "config.yaml"
            text = VALID.format(repo=repo).replace("true", '"true"')
            path.write_text(text, encoding="utf-8")
            with self.assertRaises(TypeError):
                load_config(str(path))


if __name__ == "__main__":
    unittest.main()
