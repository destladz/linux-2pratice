from config import load_config
from graph import (
    load_test_repository,
    build_graph,
    dependency_order
)
from maven import get_direct_dependencies
from visualizer import print_ascii_tree, save_plantuml


def main():
    try:
        config = load_config()

        print("\nПАРАМЕТРЫ ПРОГРАММЫ")

        for key, value in config.items():
            print(f"{key} = {value}")

        package = config["package"]

        if config["test_mode"]:
            repository_graph = load_test_repository(
                config["test_file"]
            )

            if package not in repository_graph:
                raise ValueError(f"Пакет {package} отсутствует в тестовом графе")

            def get_dependencies(name):
                return repository_graph.get(name, [])

        else:
            def get_dependencies(name):
                return get_direct_dependencies(
                    config["repository"],
                    name
                )

        print("\nПРЯМЫЕ ЗАВИСИМОСТИ")

        direct = get_dependencies(package)

        for dependency in direct:
            print(dependency)

        print("\nПОСТРОЕНИЕ ГРАФА")

        graph = build_graph(
            package,
            get_dependencies,
            config["max_depth"]
        )

        for node, dependencies in graph.items():
            print(f"{node} -> {dependencies}")

        print("\nПОРЯДОК ЗАГРУЗКИ")

        order = dependency_order(graph, package)

        for index, item in enumerate(order, start=1):
            print(f"{index}. {item}")

        if config["ascii_tree"]:
            print("\nASCII-ДЕРЕВО")
            print_ascii_tree(graph, package)

        print("\nСОЗДАНИЕ PLANTUML")

        save_plantuml(
            graph,
            config["plantuml_file"]
        )

    except (ValueError, RuntimeError, OSError) as error:
        print(f"\nОШИБКА: {error}")


if __name__ == "__main__":
    main()