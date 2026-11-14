
import json
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
    """Проверяет допустимость максимальной глубины."""
    if isinstance(max_depth, bool) or not isinstance(max_depth, int):
        raise ValueError("max_depth должен быть целым числом")

    if max_depth < MIN_DEPTH:
        raise ValueError("max_depth не может быть отрицательным")


def visit_dependency(
    package,
    depth,
    graph,
    best_depth,
    active,
    get_dependencies,
    max_depth,
):
    """Рекурсивно обрабатывает один пакет."""
    if package in active:
        return

    previous_depth = best_depth.get(package)

    if previous_depth is not None and previous_depth <= depth:
        return

    best_depth[package] = depth
    graph.setdefault(package, [])
    active.add(package)

    try:
        if depth >= max_depth:
            return

        dependencies = get_dependencies(package)

        for dependency in dependencies:
            if dependency not in graph[package]:
                graph[package].append(dependency)

            graph.setdefault(dependency, [])

            visit_dependency(
                dependency,
                depth + 1,
                graph,
                best_depth,
                active,
                get_dependencies,
                max_depth,
            )
    finally:
        active.remove(package)


def build_graph(root, get_dependencies, max_depth):
    """Строит граф зависимостей с помощью рекурсивного DFS."""
    validate_max_depth(max_depth)

    graph = {}
    best_depth = {}
    active = set()

    visit_dependency(
        root,
        MIN_DEPTH,
        graph,
        best_depth,
        active,
        get_dependencies,
        max_depth,
    )

    return graph


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
