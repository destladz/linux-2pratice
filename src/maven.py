import xml.etree.ElementTree as ET
from urllib.request import urlopen
from urllib.error import URLError, HTTPError


def get_pom_url(repository, package):
    parts = package.split(":")

    if len(parts) != 3:
        raise ValueError("Формат пакета: groupId:artifactId:version")

    group, artifact, version = parts

    group_path = group.replace(".", "/")

    return (
        f"{repository.rstrip('/')}/"
        f"{group_path}/{artifact}/{version}/"
        f"{artifact}-{version}.pom"
    )


def get_pom(repository, package):
    url = get_pom_url(repository, package)

    try:
        with urlopen(url, timeout=20) as response:
            return response.read()
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        raise RuntimeError(f"Ошибка получения POM: {error}")


def get_direct_dependencies(repository, package):
    xml_data = get_pom(repository, package)

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as error:
        raise ValueError(f"Ошибка XML: {error}")

    def tag(element):
        return element.tag.split("}")[-1]

    dependencies = []

    # Берём только непосредственный раздел dependencies.
    section = next(
        (child for child in root if tag(child) == "dependencies"),
        None
    )

    if section is None:
        return []

    for dependency in section:
        if tag(dependency) != "dependency":
            continue

        values = {
            tag(child): (child.text or "").strip()
            for child in dependency
        }

        group = values.get("groupId")
        artifact = values.get("artifactId")
        version = values.get("version")
        scope = values.get("scope", "compile")
        optional = values.get("optional", "false")

        if scope in ("test", "provided", "system", "import"):
            continue

        if optional == "true":
            continue

        if group and artifact and version and "${" not in version:
            dependencies.append(f"{group}:{artifact}:{version}")

    return sorted(set(dependencies))