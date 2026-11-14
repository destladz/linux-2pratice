
import sys
import unittest
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "src"),
)

from graph import build_graph, dependency_order
from visualizer import print_ascii_tree


class GraphTests(unittest.TestCase):
    """Тесты построения и отображения графа зависимостей."""

    def create_test_data(self):
        """Создаёт тестовый граф с циклической зависимостью."""
        return {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D", "E"],
            "D": ["A"],
            "E": [],
        }

    def test_cycle_is_handled(self):
        """Проверяет обработку циклических зависимостей."""
        data = self.create_test_data()

        graph = build_graph(
            "A",
            lambda node: data[node],
            5,
        )

        self.assertEqual(set(graph), set(data))

    def test_depth_limit(self):
        """Проверяет ограничение глубины обхода."""
        data = self.create_test_data()

        graph = build_graph(
            "A",
            lambda node: data[node],
            1,
        )

        self.assertEqual(graph["A"], ["B", "C"])
        self.assertEqual(graph["B"], [])

    def test_order(self):
        """Проверяет порядок обхода зависимостей."""
        data = self.create_test_data()

        graph = build_graph(
            "A",
            lambda node: data[node],
            5,
        )

        order = dependency_order(graph, "A")

        self.assertEqual(order[-1], "A")
        self.assertEqual(len(order), len(set(order)))

    def test_ascii_tree(self):
        """Проверяет вывод ASCII-дерева."""
        graph = {
            "A": ["B", "C"],
            "B": [],
            "C": [],
        }

        print_ascii_tree(graph, "A")


if __name__ == "__main__":
    unittest.main()
