import yaml
from pathlib import Path

DEFAULTS = {
    "package": "",
    "repository": "https://repo.maven.apache.org/maven2",
    "test_mode": False,
    "test_file": "tests/repository.json",
    "max_depth": 5,
    "ascii_tree": False,
    "plantuml_file": "dependency_graph.puml"
}

def load_config(path):
    config_path = Path(path)

    if not config_path.is_file():
        raise ValueError(f"Файл конфигурации не найден: {path}")

    data = yaml.safe_load(
        config_path.read_text(encoding="utf-8")
    ) or {}

    if not isinstance(data, dict):
        raise ValueError("Некорректный YAML")

    config = {**DEFAULTS, **data}

    if not config["package"]:
        raise ValueError("Не указано имя пакета")

    if not isinstance(config["test_mode"], bool):
        raise ValueError("test_mode должен быть true или false")

    if not isinstance(config["ascii_tree"], bool):
        raise ValueError("ascii_tree должен быть true или false")

    if not isinstance(config["max_depth"], int):
        raise ValueError("max_depth должен быть целым числом")

    if config["max_depth"] < 0:
        raise ValueError("max_depth не может быть отрицательным")

    return config