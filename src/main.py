import argparse
import json
from pathlib import Path
import sys

from config import load_config

from graph import (
    build_graph,
    load_test_graph,
    dependency_order,
    ascii_tree,
    plantuml_text
)

from maven import (
    fetch_pom,
    direct_dependencies
)

def arguments():
    parser = argparse.ArgumentParser(
        description="Maven Dependency Graph"
    )

    parser.add_argument(
        "--config",
        default="config.yaml"
    )

    return parser.parse_args()

def print_config(config):
    print("\nПараметры программы:")

    for key, value in config.items():
        print(f"{key}: {value}")

def main():
    args = arguments()

    try:
        config = load_config(args.config)

        print_config(config)

        root = config["package"]

        if config["test_mode"]:

            test_graph = load_test_graph(
                config["test_file"]
            )

            def get_deps(node):
                return test_graph.get(node, [])

        else:

            repository = config["repository"]

            def get_deps(node):
                pom = fetch_pom(repository, node)

                return direct_dependencies(pom)

        graph = build_graph(
            root,
            get_deps,
            config["max_depth"]
        )

        print("\nГраф зависимостей:")

        print(
            json.dumps(
                graph,
                ensure_ascii=False,
                indent=2
            )
        )

        print("\nПорядок загрузки:")

        order = dependency_order(graph, root)

        print(" -> ".join(order))

        if config["ascii_tree"]:

            print("\nASCII-дерево:")

            print(
                ascii_tree(graph, root)
            )

        output = Path(
            config["plantuml_file"]
        )

        output.write_text(
            plantuml_text(graph),
            encoding="utf-8"
        )

        print(
            f"\nPlantUML сохранён: {output}"
        )

    except (ValueError, RuntimeError, OSError) as error:

        print(
            f"Ошибка: {error}",
            file=sys.stderr
        )

        return 1

    return 0

if __name__ == "__main__":
    raise SystemExit(main())