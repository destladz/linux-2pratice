def print_ascii_tree(graph, root):
    print(root)

    def dfs(node, prefix, path):
        children = graph.get(node, [])

        for index, child in enumerate(children):
            last = index == len(children) - 1

            branch = "└── " if last else "├── "
            print(prefix + branch + child)

            if child in path:
                print(prefix + "    ↳ цикл")
                continue

            extension = "    " if last else "│   "

            dfs(child, prefix + extension, path | {child})

    dfs(root, "", {root})


def save_plantuml(graph, filename):
    lines = [
        "@startuml",
        "left to right direction",
        "skinparam packageStyle rectangle"
    ]

    for package, dependencies in graph.items():
        for dependency in dependencies:
            lines.append(f'"{package}" --> "{dependency}"')

    lines.append("@enduml")

    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    print(f"PlantUML сохранён в {filename}")