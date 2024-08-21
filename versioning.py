from warnings import catch_warnings

import exceptions
import helpers
import re

from exceptions import BooException

VERSION_COMPONENTS = {
    "major": 10000,
    "minor": 100,
    "micro": 1
}

VERSION_PATTERN = r'\* Version:\s*([^\s\*]+)'


def extract_versions(plugin_absolute_paths: list) -> dict:
    result = {}

    for path in plugin_absolute_paths:
        try:
            main_file_abspath = helpers.get_main_file_abspath(path)
            result[path] = extract_version_from_file(main_file_abspath)
        except BooException as e:
            result[path] = str(e)

    return result


def extract_version_from_file(path: str) -> str:
    try:
        with open(path, 'r') as file:
            content = file.read()
            match = re.search(VERSION_PATTERN, content)
            if match:
                return match.group(1)
            raise exceptions.SearchNotFound
    except IOError as e:
        raise exceptions.BooException(f"An error occurred while reading the file {path}: {e}")


def set_version_to_file(path: str, dn_version: str) -> None:
    try:
        with open(path, 'r') as file:
            file_content = file.read()
    except IOError as e:
        raise exceptions.BooException(f"An error occurred while reading the file {path}: {e}")

    updated_content = re.sub(VERSION_PATTERN, f"* Version: {dn_version}", file_content)

    try:
        with open(path, 'w') as file:
            file.write(updated_content)
    except IOError as e:
        raise exceptions.BooException(f"An error occurred while writing the file {path}: {e}")


def version_to_int(dot_notation_version: str) -> int:
    version_pieces = dot_notation_version.split('.')

    try:
        parse_version_component = lambda: int(version_pieces.pop(0)) if len(version_pieces) else 0

        major = parse_version_component() * VERSION_COMPONENTS.get('major')
        minor = parse_version_component() * VERSION_COMPONENTS.get('minor')
        micro = parse_version_component() * VERSION_COMPONENTS.get('micro')

        return major + minor + micro
    except ValueError:
        raise exceptions.InvalidArgumentError(dot_notation_version)


def version_to_dn(version_int: int) -> str:
    major = version_int // VERSION_COMPONENTS['major']
    version_int %= VERSION_COMPONENTS['major']

    minor = version_int // VERSION_COMPONENTS['minor']
    version_int %= VERSION_COMPONENTS['minor']

    micro = version_int // VERSION_COMPONENTS['micro']

    return f"{major}.{minor}.{micro}"


def update_plugin_version(plugin_absolute_path: str, increase: int, decrease: int):
    plugin_main_file = helpers.get_main_file_abspath(plugin_absolute_path)
    plugin_dn_version = extract_version_from_file(plugin_main_file)
    plugin_int_version = version_to_int(plugin_dn_version)
    version_delta = increase - decrease
    new_version = plugin_int_version + version_delta
    new_dn_version = version_to_dn(new_version)
    set_version_to_file(plugin_main_file, new_dn_version)
