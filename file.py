import os
import zipfile
import wppcpy

import exceptions
from helpers import MAIN_FILES
from version import Version


class Zip:
    @staticmethod
    def create(directory_path: str, output_zip_path: str) -> None:
        directory_name = os.path.basename(directory_path)

        with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for root, _, files in os.walk(directory_path):
                for file_name in files:
                    full_file_path = os.path.join(root, file_name)
                    relative_file_path = os.path.join(str(directory_name),
                                                      os.path.relpath(str(full_file_path), directory_path))
                    zip_file.write(str(full_file_path), relative_file_path)


class Plugin:
    def __init__(self, path: str) -> None:
        self.validate(path)
        self._path = path

    @property
    def plugin(self) -> str:
        return os.path.join(self._path, self.main_file(self._path))

    @property
    def version(self) -> Version:
        return Version(self.plugin)

    @property
    def full_path(self) -> str:
        return os.path.abspath(self._path)

    @property
    def path(self) -> str:
        return self._path

    @property
    def name(self) -> str:
        return os.path.basename(self.path)

    @staticmethod
    def abspaths(directory_path: str) -> list:
        plugins = [plugin.full_path for plugin in Plugin.list(directory_path)]

        return sorted(plugins)

    @staticmethod
    def main_file(path: str) -> str:
        for main_file in MAIN_FILES:
            if os.path.isfile(os.path.join(path, main_file)):
                return main_file

        plugin_name = os.path.basename(path)
        raise exceptions.SearchNotFound(f"Main file does not exist for the '{plugin_name}'")

    @staticmethod
    def filter(abspaths: list[str], include: list[str], exclude: list[str]) -> list[str]:
        f = lambda abspaths, callback: [_ for _ in abspaths if callback(_)]

        if include:
            callback: callable(str) = lambda path: any(_.strip("/") == os.path.basename(path) for _ in include)
            abspaths: list[str] = f(abspaths, callback)

        if exclude:
            callback: callable(str) = lambda path: all(_.strip("/") != os.path.basename(path) for _ in exclude)
            abspaths: list[str] = f(abspaths, callback)

        return abspaths

    def update(self, content: str) -> None:
        try:
            with open(self.plugin, 'w') as plugin:
                plugin.write(content)
        except IOError as e:
            raise exceptions.BooException(f"An error occurred while writing the file '{plugin}': {e}")

    def content(self) -> str:
        try:
            with open(self.plugin, 'r') as plugin:
                content = plugin.read()
        except IOError as e:
            raise exceptions.BooException(f"An error occurred while reading the file '{plugin}': {e}")

        return content

    @staticmethod
    def validate(path: str) -> bool:
        main_file_name = "init.php"

        plugin_constraints = [
            wppcpy.constraints.file.MainFile(path, files=main_file_name),
            wppcpy.constraints.header.PluginName(path, main_file_name=main_file_name),
            wppcpy.constraints.header.Version(path, main_file_name=main_file_name),
        ]

        try:
            return all(cons.validate() for cons in plugin_constraints)
        except wppcpy.exceptions.base.PcpyException:
            return False


    @staticmethod
    def list(path: str) -> list:
        plugins = [Plugin(os.path.join(path, _))
                   for _ in sorted(os.listdir(path))
                   if Plugin.validate(os.path.join(path, _))]

        return plugins
