import json
from pathlib import Path


def load_test_repository(filename):
    path = Path(filename)

    if not path.exists():
        raise ValueError("Тестовый репозиторий не найден")

    with open(path, "r", encoding="utf-8") as file:
        graph = json.load(file)

    if not isinstance(graph, dict):
        raise ValueError("Тестовый граф должен быть JSON-объектом")

    for package, dependencies in graph.items():
        if not package.isalpha() or not package.isupper():
            raise ValueError(f"Некорректное имя пакета: {package}")

        if not isinstance(dependencies, list):
            raise ValueError(f"Зависимости {package} должны быть списком")

        for dependency in dependencies:
            if (
                not isinstance(dependency, str)
                or not dependency.isalpha()
                or not dependency.isupper()
            ):
                raise ValueError(f"Некорректная зависимость: {dependency}")

    for dependencies in graph.values():
        for dependency in dependencies:
            graph.setdefault(dependency, [])

    return graph


def build_graph(root, get_dependencies, max_depth):
    graph = {}
    visited = set()
    active = set()

    def dfs(package, depth):
        if package in visited or package in active:
            return

        active.add(package)
        graph.setdefault(package, [])

        if depth < max_depth:
            dependencies = get_dependencies(package)
        else:
            dependencies = []

        for dependency in dependencies:
            if dependency not in graph[package]:
                graph[package].append(dependency)

            graph.setdefault(dependency, [])

            dfs(dependency, depth + 1)

        active.remove(package)
        visited.add(package)

    dfs(root, 0)

    return graph


def dependency_order(graph, root):
    result = []
    visited = set()
    active = set()

    def dfs(package):
        if package in visited or package in active:
            return

        active.add(package)

        for dependency in graph.get(package, []):
            dfs(dependency)

        active.remove(package)
        visited.add(package)
        result.append(package)

    dfs(root)

    return result