from config import load_config
from graph import (
    load_test_repository,
    build_graph,
    dependency_order,
)
from maven import get_direct_dependencies
from visualizer import print_ascii_tree, save_plantuml


def print_config(config):
    """Выводит параметры программы."""
    print("\nПАРАМЕТРЫ ПРОГРАММЫ")
    for key, value in config.items():
        print(f"{key} = {value}")


def create_dependency_provider(config):
    """Создаёт функцию получения зависимостей."""
    if config["test_mode"]:
        repository = load_test_repository(config["test_file"])
        package = config["package"]

        if package not in repository:
            raise ValueError(
                f"Пакет {package} отсутствует в тестовом графе"
            )

        return lambda name: repository.get(name, [])

    def get_dependencies(name):
        """Получает зависимости из Maven-репозитория."""
        return get_direct_dependencies(
            config["repository"],
            name,
        )

    return get_dependencies


def print_direct_dependencies(package, get_dependencies):
    """Выводит прямые зависимости пакета."""
    print("\nПРЯМЫЕ ЗАВИСИМОСТИ")
    dependencies = get_dependencies(package)

    for dependency in dependencies:
        print(dependency)


def print_graph(graph):
    """Выводит построенный граф зависимостей."""
    print("\nПОСТРОЕНИЕ ГРАФА")

    for node, dependencies in graph.items():
        print(f"{node} -> {dependencies}")


def print_loading_order(graph, package):
    """Выводит порядок загрузки зависимостей."""
    print("\nПОРЯДОК ЗАГРУЗКИ")

    order = dependency_order(graph, package)

    for index, item in enumerate(order, start=1):
        print(f"{index}. {item}")


def visualize_graph(graph, package, config):
    """Создаёт текстовое и графическое представление."""
    if config["ascii_tree"]:
        print("\nASCII-ДЕРЕВО")
        print_ascii_tree(graph, package)

    print("\nСОЗДАНИЕ PLANTUML")
    save_plantuml(graph, config["plantuml_file"])


def main():
    """Запускает анализ зависимостей."""
    try:
        config = load_config()
        print_config(config)

        get_dependencies = create_dependency_provider(config)
        package = config["package"]

        print_direct_dependencies(package, get_dependencies)

        graph = build_graph(
            package,
            get_dependencies,
            config["max_depth"],
        )

        print_graph(graph)
        print_loading_order(graph, package)
        visualize_graph(graph, package, config)

    except (ValueError, RuntimeError, OSError) as error:
        print(f"\nОШИБКА: {error}")


if __name__ == "__main__":
    main()
