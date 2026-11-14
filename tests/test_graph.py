import io
import unittest
from contextlib import redirect_stdout

from src.graph import build_graph, dependency_order
from src.visualizer import print_ascii_tree


def create_test_data():
    """Создаёт тестовый граф с циклической зависимостью."""
    return {
        "A": ["B", "C"],
        "B": ["D"],
        "C": ["D", "E"],
        "D": ["A"],
        "E": [],
    }


class GraphTests(unittest.TestCase):
    """Тесты построения и отображения графа зависимостей."""

    def test_cycle_is_handled(self):
        """Проверяет обработку циклических зависимостей."""
        data = create_test_data()

        graph = build_graph(
            "A",
            lambda node: data[node],
            5,
        )

        self.assertEqual(set(graph), set(data))
        self.assertIn("A", graph["D"])

    def test_depth_limit(self):
        """Проверяет ограничение глубины обхода."""
        data = create_test_data()

        graph = build_graph(
            "A",
            lambda node: data[node],
            1,
        )

        self.assertEqual(graph["A"], ["B", "C"])
        self.assertEqual(graph["B"], [])
        self.assertEqual(graph["C"], [])

    def test_order(self):
        """Проверяет порядок обхода зависимостей."""
        data = create_test_data()

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

        output = io.StringIO()

        with redirect_stdout(output):
            print_ascii_tree(graph, "A")

        self.assertIn("A", output.getvalue())
        self.assertIn("B", output.getvalue())
        self.assertIn("C", output.getvalue())

    def test_negative_depth(self):
        """Проверяет обработку отрицательной глубины."""
        with self.assertRaises(ValueError):
            build_graph("A", lambda node: [], -1)

    def test_invalid_depth_type(self):
        """Проверяет обработку неправильного типа глубины."""
        with self.assertRaises(ValueError):
            build_graph("A", lambda node: [], "5")


if __name__ == "__main__":
    unittest.main()
