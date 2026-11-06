def build_graph(root, get_dependencies, max_depth):
    graph = {}
    visited = set()
    active = set()

    def visit(node, depth):
        if node in visited or depth > max_depth:
            return

        if node in active:
            return

        active.add(node)

        if depth < max_depth:
            dependencies = get_dependencies(node)
        else:
            dependencies = []

        graph.setdefault(node, [])

        for dependency in dependencies:
            graph[node].append(dependency)
            graph.setdefault(dependency, [])

            if dependency not in active:
                visit(dependency, depth + 1)

        active.remove(node)
        visited.add(node)

    visit(root, 0)

    return graph

def load_test_graph(path):
    import json
    from pathlib import Path

    file_path = Path(path)

    if not file_path.is_file():
        raise ValueError(
            f"Тестовый файл не найден: {path}"
        )

    data = json.loads(
        file_path.read_text(encoding="utf-8")
    )

    if not isinstance(data, dict):
        raise ValueError("Неверный формат тестового графа")

    return {
        str(key): list(value)
        for key, value in data.items()
    }

def dependency_order(graph, root):
    result = []
    visited = set()
    active = set()

    def visit(node):
        if node in visited or node in active:
            return

        active.add(node)

        for child in graph.get(node, []):
            visit(child)

        active.remove(node)
        visited.add(node)
        result.append(node)

    visit(root)

    return result

def ascii_tree(graph, root):
    lines = [root]

    def walk(node, prefix, path):
        children = graph.get(node, [])

        for index, child in enumerate(children):
            last = index == len(children) - 1

            branch = "└── " if last else "├── "

            lines.append(prefix + branch + child)

            if child not in path:
                extension = "    " if last else "│   "

                walk(
                    child,
                    prefix + extension,
                    path | {child}
                )

            else:
                lines.append(
                    prefix + "    ↳ cycle"
                )

    walk(root, "", {root})

    return "\n".join(lines)

def plantuml_text(graph):
    lines = [
        "@startuml",
        "left to right direction"
    ]

    for node, dependencies in graph.items():
        for dependency in dependencies:
            lines.append(
                f'"{node}" --> "{dependency}"'
            )

    lines.append("@enduml")

    return "\n".join(lines) + "\n"