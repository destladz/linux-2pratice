
from pathlib import Path
from urllib.parse import urlparse

import yaml


EXPECTED_COORDINATE_PARTS = 3
VALID_URL_SCHEMES = ("http", "https")

REQUIRED_KEYS = (
    "package",
    "repository",
    "test_mode",
    "test_file",
    "max_depth",
    "ascii_tree",
    "plantuml_file",
)


def get_project_root():
    """Возвращает корневую папку проекта."""
    return Path(__file__).resolve().parent.parent


def validate_required_keys(config):
    """Проверяет наличие обязательных параметров."""
    for key in REQUIRED_KEYS:
        if key not in config:
            raise ValueError(f"Отсутствует параметр {key}")


def validate_package(config):
    """Проверяет название или координаты пакета."""
    package = config["package"]

    if not isinstance(package, str) or not package.strip():
        raise ValueError("package должен быть непустой строкой")

    if config["test_mode"]:
        if not package.isascii() or not package.isalpha():
            raise ValueError("Имя тестового пакета должно быть латинским")
        if not package.isupper():
            raise ValueError("Имя тестового пакета должно быть заглавным")
        return

    parts = package.split(":")
    if len(parts) != EXPECTED_COORDINATE_PARTS:
        raise ValueError("Неверный формат координат пакета")

    if not all(parts):
        raise ValueError("Все части координат пакета должны быть заполнены")


def validate_repository(config):
    """Проверяет URL Maven-репозитория."""
    repository = config["repository"]

    if not isinstance(repository, str):
        raise ValueError("repository должен быть строкой")

    parsed = urlparse(repository)

    if parsed.scheme not in VALID_URL_SCHEMES or not parsed.netloc:
        raise ValueError("Некорректный URL репозитория")


def validate_options(config):
    """Проверяет логические и числовые настройки."""
    boolean_keys = ("test_mode", "ascii_tree")

    for key in boolean_keys:
        if not isinstance(config[key], bool):
            raise ValueError(f"{key} должен быть true или false")

    depth = config["max_depth"]

    if isinstance(depth, bool) or not isinstance(depth, int):
        raise ValueError("max_depth должен быть целым числом")

    if depth < 0:
        raise ValueError("max_depth не может быть отрицательным")


def validate_output_file(config):
    """Проверяет имя файла PlantUML."""
    filename = config["plantuml_file"]

    if not isinstance(filename, str) or not filename.strip():
        raise ValueError("plantuml_file должен быть непустой строкой")

    if Path(filename).suffix != ".puml":
        raise ValueError("Файл PlantUML должен иметь расширение .puml")


def validate_test_file(config):
    """Проверяет наличие файла с тестовыми зависимостями."""
    filename = config["test_file"]

    if not isinstance(filename, str) or not filename.strip():
        raise ValueError("Некорректный test_file")

    test_path = Path(filename)

    if not test_path.is_absolute():
        test_path = get_project_root() / test_path

    if not test_path.is_file():
        raise ValueError(f"Тестовый файл не найден: {test_path}")

    config["test_file"] = str(test_path)


def load_config(filename="config.yaml"):
    """Загружает настройки и проверяет их корректность."""
    config_path = Path(filename)

    if not config_path.is_absolute():
        config_path = get_project_root() / config_path

    if not config_path.is_file():
        raise ValueError(f"Файл конфигурации не найден: {config_path}")

    try:
        with config_path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except yaml.YAMLError as error:
        raise ValueError(f"Ошибка YAML: {error}") from error

    if not isinstance(config, dict):
        raise ValueError("Конфигурация должна быть словарём")

    validate_required_keys(config)
    validate_options(config)
    validate_package(config)
    validate_repository(config)
    validate_output_file(config)

    if config["test_mode"]:
        validate_test_file(config)

    return config
