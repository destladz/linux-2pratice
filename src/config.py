from pathlib import Path
from urllib.parse import urlparse
import yaml


def load_config(filename="config.yaml"):
    path = Path(__file__).resolve().parent.parent / filename

    if not path.exists():
        raise ValueError(f"Файл {filename} не найден")

    try:
        with open(path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except yaml.YAMLError as error:
        raise ValueError(f"Ошибка YAML: {error}")

    if not isinstance(config, dict):
        raise ValueError("Конфигурация должна быть словарём")

    required = [
        "package",
        "repository",
        "test_mode",
        "test_file",
        "max_depth",
        "ascii_tree",
        "plantuml_file"
    ]

    for key in required:
        if key not in config:
            raise ValueError(f"Отсутствует параметр {key}")

    if not isinstance(config["package"], str) or not config["package"].strip():
        raise ValueError("package должен быть непустой строкой")

    if not isinstance(config["test_mode"], bool):
        raise ValueError("test_mode должен быть true или false")

    if not isinstance(config["ascii_tree"], bool):
        raise ValueError("ascii_tree должен быть true или false")

    depth = config["max_depth"]

    if isinstance(depth, bool) or not isinstance(depth, int) or depth < 0:
        raise ValueError("max_depth должен быть целым числом от 0")

    if not isinstance(config["repository"], str):
        raise ValueError("repository должен быть строкой")

    parsed = urlparse(config["repository"])

    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("Некорректный URL репозитория")

    if not isinstance(config["test_file"], str) or not config["test_file"].strip():
        raise ValueError("Некорректный test_file")

    if not isinstance(config["plantuml_file"], str):
        raise ValueError("plantuml_file должен быть строкой")

    if not config["plantuml_file"].endswith(".puml"):
        raise ValueError("Файл PlantUML должен иметь расширение .puml")

    if config["test_mode"]:
        if not config["package"].isalpha() or not config["package"].isupper():
            raise ValueError("Тестовые пакеты должны называться большими латинскими буквами")

        test_path = Path(__file__).resolve().parent.parent / config["test_file"]

        if not test_path.is_file():
            raise ValueError(f"Тестовый файл не найден: {test_path}")

        config["test_file"] = str(test_path)

    else:
        parts = config["package"].split(":")

        if len(parts) != 3 or not all(parts):
            raise ValueError(
                "В реальном режиме package должен иметь формат groupId:artifactId:version"
            )

    return config