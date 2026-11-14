
import json
from dataclasses import dataclass
from pathlib import Path


MIN_DEPTH = 0


def is_valid_package_name(name):
    """Проверяет имя тестового пакета."""
    return (
        isinstance(name, str)
        and name.isascii()
        and name.isalpha()
        and name.isupper()
    )


def validate_repository(graph):
    """Проверяет структуру и содержимое тестового графа."""
    if not isinstance(graph, dict):
        raise ValueError("Тестовый граф должен быть JSON-объектом")

    for package, dependencies in graph.items():
        if not is_valid_package_name(package):
            raise ValueError(f"Некорректное имя пакета: {package}")

        if not isinstance(dependencies, list):
            raise ValueError(
                f"Зависимости {package} должны быть списком"
            )

        for dependency in dependencies:
            if not is_valid_package_name(dependency):
                raise ValueError(
                    f"Некорректная зависимость: {dependency}"
                )


def add_missing_packages(graph):
    """Добавляет пакеты, у которых нет собственных зависимостей."""
    missing = {
        dependency
        for dependencies in graph.values()
        for dependency in dependencies
        if dependency not in graph
    }

    for package in sorted(missing):
        graph[package] = []


def load_test_repository(filename):
    """Загружает и проверяет тестовый граф из JSON."""
    path = Path(filename)

    if not path.is_file():
        raise ValueError(
            f"Тестовый репозиторий не найден: {path}"
        )

    try:
        with path.open("r", encoding="utf-8") as file:
            graph = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Ошибка JSON: {error}"
        ) from error
    except OSError as error:
        raise ValueError(
            f"Не удалось прочитать тестовый файл: {error}"
        ) from error

    validate_repository(graph)
    add_missing_packages(graph)

    return graph


def validate_max_depth(max_depth):
    """Проверяет допустимую максимальную глубину."""
    if isinstance(max_depth, bool) or not isinstance(max_depth, int):
        raise ValueError("max_depth должен быть целым числом")

    if max_depth < MIN_DEPTH:
        raise ValueError("max_depth не может быть отрицательным")


@dataclass
class TraversalContext:
    """Хранит общее состояние обхода графа."""

    graph: dict
    best_depth: dict
    active: set
    get_dependencies: object
    max_depth: int


def visit_dependencies(package, depth, dependencies, context):
    """Обрабатывает зависимости текущего пакета."""
    for dependency in dependencies:
        if dependency not in context.graph[package]:
            context.graph[package].append(dependency)

        context.graph.setdefault(dependency, [])

        visit_dependency(
            dependency,
            depth + 1,
            context,
        )


def visit_dependency(package, depth, context):
    """Рекурсивно обрабатывает один пакет."""
    if package in context.active:
        return

    previous_depth = context.best_depth.get(package)
    if previous_depth is not None and previous_depth <= depth:
        return

    context.best_depth[package] = depth
    context.graph.setdefault(package, [])
    context.active.add(package)

    try:
        if depth < context.max_depth:
            dependencies = context.get_dependencies(package)
            visit_dependencies(
                package,
                depth,
                dependencies,
                context,
            )
    finally:
        context.active.remove(package)


def build_graph(root, get_dependencies, max_depth):
    """Строит граф зависимостей с помощью рекурсивного DFS."""
    validate_max_depth(max_depth)

    context = TraversalContext(
        graph={},
        best_depth={},
        active=set(),
        get_dependencies=get_dependencies,
        max_depth=max_depth,
    )

    visit_dependency(root, MIN_DEPTH, context)

    return context.graph


def dfs_order(package, graph, visited, active, result):
    """Рекурсивно определяет порядок обхода зависимостей."""
    if package in visited or package in active:
        return

    active.add(package)

    for dependency in graph.get(package, []):
        dfs_order(
            dependency,
            graph,
            visited,
            active,
            result,
        )

    active.remove(package)
    visited.add(package)
    result.append(package)


def dependency_order(graph, root):
    """Возвращает порядок обхода зависимостей."""
    result = []
    visited = set()
    active = set()

    dfs_order(root, graph, visited, active, result)

    return result
