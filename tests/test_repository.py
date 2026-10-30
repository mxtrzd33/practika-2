"""Tests for the custom text test-repository parser."""

import tempfile
import unittest
from pathlib import Path

from src.test_repository import load_test_repository


class TestRepositoryTests(unittest.TestCase):
    """Validate accepted graph data and malformed input handling."""

    def test_parse_edges(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "repo.txt"
            path.write_text("A:B,C\\nB:\\n", encoding="utf-8")
            graph = load_test_repository(str(path))
            self.assertEqual(graph["A"], ["B", "C"])

    def test_reject_invalid_name(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "repo.txt"
            path.write_text("abc:B\\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_test_repository(str(path))

    def test_reject_duplicate(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "repo.txt"
            path.write_text("A:B\\nA:C\\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_test_repository(str(path))


if __name__ == "__main__":
    unittest.main()
