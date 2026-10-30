"""Tests for Graphviz DOT output."""

import tempfile
import unittest
from pathlib import Path

from src.render import save_dot, to_dot


class RenderTests(unittest.TestCase):
    """Check directed edges, isolated nodes, and DOT file output."""

    def test_dot_contains_edge(self):
        self.assertIn('"A" -> "B"', to_dot({"A": ["B"]}))

    def test_dot_contains_isolated_node(self):
        self.assertIn('"Z";', to_dot({"Z": []}))

    def test_save_dot(self):
        with tempfile.TemporaryDirectory() as folder:
            path = save_dot({"A": ["B"]}, folder)
            self.assertTrue(path.is_file())


if __name__ == "__main__":
    unittest.main()
