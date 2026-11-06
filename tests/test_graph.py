import sys
import unittest
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src")
)

from graph import (
    build_graph,
    dependency_order,
    ascii_tree
)

class GraphTests(unittest.TestCase):

    def setUp(self):
        self.data = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D", "E"],
            "D": ["A"],
            "E": []
        }

    def test_cycle_is_handled(self):
        graph = build_graph(
            "A",
            lambda node: self.data[node],
            5
        )

        self.assertEqual(
            set(graph),
            set(self.data)
        )

    def test_depth_limit(self):
        graph = build_graph(
            "A",
            lambda node: self.data[node],
            1
        )

        self.assertEqual(
            graph["A"],
            ["B", "C"]
        )

        self.assertEqual(
            graph["B"],
            []
        )

    def test_order(self):
        graph = build_graph(
            "A",
            lambda node: self.data[node],
            5
        )

        order = dependency_order(graph, "A")

        self.assertEqual(
            order[-1],
            "A"
        )

    def test_ascii_tree(self):
        graph = build_graph(
            "A",
            lambda node: self.data[node],
            5
        )

        tree = ascii_tree(graph, "A")

        self.assertIn("A", tree)

if __name__ == "__main__":
    unittest.main()