
import xml.etree.ElementTree as ElementTree
from urllib.request import urlopen
from urllib.error import URLError


REQUEST_TIMEOUT = 20
EXPECTED_COORDINATE_PARTS = 3
EXCLUDED_SCOPES = ("test", "provided", "system", "import")
DEFAULT_SCOPE = "compile"


def validate_coordinates(package):
    """Проверяет координаты Maven-пакета."""
    if not isinstance(package, str):
        raise ValueError("Координаты пакета должны быть строкой")

    parts = package.split(":")

    if len(parts) != EXPECTED_COORDINATE_PARTS:
        raise ValueError(
            "Формат пакета: groupId:artifactId:version"
        )

    if not all(part.strip() for part in parts):
        raise ValueError("Координаты пакета не должны быть пустыми")

    return parts


def get_pom_url(repository, package):
    """Формирует URL POM-файла по координатам пакета."""
    group, artifact, version = validate_coordinates(package)
    group_path = group.replace(".", "/")

    return (
        f"{repository.rstrip('/')}/"
        f"{group_path}/{artifact}/{version}/"
        f"{artifact}-{version}.pom"
    )


def get_pom(repository, package):
    """Загружает POM-файл из Maven-репозитория."""
    url = get_pom_url(repository, package)

    try:
        with urlopen(url, timeout=REQUEST_TIMEOUT) as response:
            return response.read()
    except (URLError, TimeoutError, OSError) as error:
        raise RuntimeError(
            f"Ошибка получения POM: {error}"
        ) from error


def get_xml_tag(element):
    """Возвращает имя XML-тега без пространства имён."""
    return element.tag.split("}")[-1]


def parse_xml(xml_data):
    """Преобразует XML-данные в дерево элементов."""
    try:
        return ElementTree.fromstring(xml_data)
    except ElementTree.ParseError as error:
        raise ValueError(
            f"Ошибка разбора XML: {error}"
        ) from error


def find_dependencies_section(root):
    """Находит раздел прямых зависимостей проекта."""
    for child in root:
        if get_xml_tag(child) == "dependencies":
            return child

    return None


def extract_dependency_values(dependency):
    """Извлекает поля одной зависимости."""
    return {
        get_xml_tag(child): (child.text or "").strip()
        for child in dependency
    }


def is_valid_dependency(values):
    """Проверяет, подходит ли зависимость для добавления."""
    group = values.get("groupId")
    artifact = values.get("artifactId")
    version = values.get("version")
    scope = values.get("scope", DEFAULT_SCOPE)
    optional = values.get("optional", "false")

    if scope in EXCLUDED_SCOPES:
        return False

    if optional.lower() == "true":
        return False

    if not group or not artifact or not version:
        return False

    if "${" in version:
        return False

    return True


def format_dependency(values):
    """Формирует координаты зависимости."""
    return (
        f"{values['groupId']}:"
        f"{values['artifactId']}:"
        f"{values['version']}"
    )


def extract_direct_dependencies(section):
    """Извлекает прямые зависимости из раздела XML."""
    if section is None:
        return []

    dependencies = []

    for dependency in section:
        if get_xml_tag(dependency) != "dependency":
            continue

        values = extract_dependency_values(dependency)

        if is_valid_dependency(values):
            dependencies.append(format_dependency(values))

    return sorted(set(dependencies))


def get_direct_dependencies(repository, package):
    """Получает прямые зависимости Maven-пакета."""
    xml_data = get_pom(repository, package)
    root = parse_xml(xml_data)
    section = find_dependencies_section(root)

    return extract_direct_dependencies(section)
