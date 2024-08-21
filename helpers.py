from typing import Any
import os
import zipfile
import subprocess
import click

import exceptions
import versioning

MAIN_FILES = ("init.php", "index.php")


def get_plugin_paths(directory_path: str) -> list:
    """Return a list of plugin directories sorted by name."""
    validate_path(directory_path)
    absolute_path = os.path.abspath(directory_path)
    plugins = [os.path.join(absolute_path, plugin) for plugin in os.listdir(absolute_path)]
    return sorted(plugins)


def validate_path(path: str) -> bool:
    """Validate if the given path is a directory."""
    if not os.path.isdir(path):
        raise exceptions.InvalidDirectoryError
    return True


def get_main_file_abspath(plugin_absolute_path: str) -> str:
    for main_file in MAIN_FILES:
        main_file_absolute_path = os.path.join(plugin_absolute_path, main_file)

        if os.path.isfile(main_file_absolute_path):
            return main_file_absolute_path

    plugin_name = os.path.basename(plugin_absolute_path)
    raise exceptions.SearchNotFound(f"Main file does not exist for the '{plugin_name}'.")


def prepare_plugins_report(path_version_dict: dict) -> list:
    """Prepare a report with plugin names and versions."""
    result = []

    for path, dn_version in path_version_dict.items():
        try:
            int_version = versioning.version_to_int(dot_notation_version=dn_version)
        except exceptions.BooException as e:
            int_version = str(e)

        result.append([os.path.basename(path), dn_version, int_version])
    return result


def get_filtered_plugin_paths(path, include, exclude):
    """Get plugin paths filtered by include and exclude lists."""
    plugin_absolute_paths = get_plugin_paths(path)

    if include:
        plugin_absolute_paths = [p for p in plugin_absolute_paths if
                                 any(inc.strip("/") == os.path.basename(p) for inc in include)]

    if exclude:
        plugin_absolute_paths = [p for p in plugin_absolute_paths if
                                 all(exc.strip("/") != os.path.basename(p) for exc in exclude)]

    return plugin_absolute_paths


def update_plugin(plugin_absolute_path, increase, decrease):
    """Update plugin version and return message."""
    increase_as_int = versioning.version_to_int(increase)
    decrease_as_int = versioning.version_to_int(decrease)
    main_file = get_main_file_abspath(plugin_absolute_path)
    old_version = versioning.extract_version_from_file(main_file)
    versioning.update_plugin_version(plugin_absolute_path, increase_as_int, decrease_as_int)
    new_version = versioning.extract_version_from_file(main_file)

    return {
        "plugin_name": os.path.basename(plugin_absolute_path),
        "old_version": old_version,
        "new_version": new_version,
    }

def stylize(value: Any) -> str:
    return click.style(value, fg='green', bold=True)

def prepare_update_message(plugin_name, old_version, new_version, color: bool = False):
    text_formatter = lambda x, fg='green', bold=True: click.style(x, fg=fg, bold=bold)

    message = f"{plugin_name} has been updated from {old_version} to version {new_version}"

    if color:
        plugin_name = text_formatter(plugin_name)
        old_version = text_formatter(old_version, fg='yellow')
        new_version = text_formatter(new_version)
        message = click.style(f"{plugin_name} has been updated from {old_version} to version {new_version}", fg='green')

    return message

def commit(add: list, message: str) -> None:
    subprocess.run(["git", "add", *add], check=True)
    subprocess.run(["git", "commit", "-m", message, "--quiet"], check=True)

def create_zip(plugin_directory, zip_path):
    base_name = os.path.basename(plugin_directory)
    temp_zip_path = zip_path

    with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(plugin_directory):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.join(str(base_name), str(os.path.relpath(str(file_path), plugin_directory)))
                zipf.write(str(file_path), arcname)

