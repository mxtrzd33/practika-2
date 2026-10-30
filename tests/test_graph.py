"""Tests for graph construction and recursive breadth-first traversal."""

import unittest

from src.graph import (
    build_dependency_graph,
    recursive_bfs,
)


from src.reverse_dependencies import reachable_reverse, reverse_graph


class GraphTests(unittest.TestCase):
    """Test paths, cycles, filtering, and reverse edges."""

    def setUp(self):
        self.graph = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D", "E"],
            "D": [],
            "E": ["A"],
        }

    def test_bfs_reaches_transitive_nodes(self):
        result = recursive_bfs(self.graph, "A")
        self.assertEqual(set(result), {"A", "B", "C", "D", "E"})

    def test_bfs_handles_cycle(self):
        result = recursive_bfs(self.graph, "A")
        self.assertEqual(len(result), 5)

    def test_filter_excludes_matching_package(self):
        result = recursive_bfs(self.graph, "A", "C")
        self.assertNotIn("C", result)
        self.assertNotIn("C", result["A"])

    def test_missing_start(self):
        with self.assertRaises(LookupError):
            recursive_bfs(self.graph, "Z")

    def test_reverse_graph(self):
        result = reverse_graph(self.graph)
        self.assertIn("A", result["E"])
        self.assertIn("B", result["D"])

    def test_reverse_reachability(self):
        result = reachable_reverse(self.graph, "D")
        self.assertIn("A", result)
        self.assertIn("C", result)

    def test_build_graph_resolves_known_packages(self):
        packages = {
            "app": {"dependencies": ["lib>=1", "absent"]},
            "lib": {"dependencies": []},
        }
        self.assertEqual(build_dependency_graph(packages)["app"], ["lib"])


if __name__ == "__main__":
    unittest.main()
