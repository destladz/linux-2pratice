from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import xml.etree.ElementTree as ET

def coordinate_parts(coordinate):
    parts = coordinate.split(":")

    if len(parts) != 3 or not all(parts):
        raise ValueError(
            "Формат пакета: groupId:artifactId:version"
        )

    return parts

def pom_url(repository, coordinate):
    group, artifact, version = coordinate_parts(coordinate)

    group_path = group.replace(".", "/")

    return (
        f"{repository.rstrip('/')}/"
        f"{group_path}/{artifact}/{version}/"
        f"{artifact}-{version}.pom"
    )

def fetch_pom(repository, coordinate):
    url = pom_url(repository, coordinate)

    try:
        with urlopen(url, timeout=20) as response:
            return response.read()

    except (HTTPError, URLError, TimeoutError) as error:
        raise RuntimeError(
            f"Не удалось получить POM: {error}"
        )

def direct_dependencies(xml_data):
    try:
        root = ET.fromstring(xml_data)

    except ET.ParseError as error:
        raise ValueError(
            f"Ошибка XML: {error}"
        )

    result = []

    for element in root.iter():

        if element.tag.endswith("dependencies"):

            for dep in list(element):

                if not dep.tag.endswith("dependency"):
                    continue

                values = {}

                for child in list(dep):
                    name = child.tag.split("}")[-1]
                    values[name] = (child.text or "").strip()

                group = values.get("groupId", "")
                artifact = values.get("artifactId", "")
                version = values.get("version", "")
                scope = values.get("scope", "compile")
                optional = values.get("optional", "false")

                if (
                    group
                    and artifact
                    and version
                    and optional != "true"
                    and scope not in [
                        "test",
                        "provided",
                        "system",
                        "import"
                    ]
                ):
                    result.append(
                        f"{group}:{artifact}:{version}"
                    )

    return sorted(set(result))