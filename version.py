import os.path
import re
from typing import List, Union

import exceptions
import file


class Version:
    FACTORS = [10000, 100, 1]
    PATTERN = r'\* Version:\s*([^\s\*]+)'

    def __init__(self, plugin: str):
        file.Plugin.validate(os.path.dirname(plugin))
        self._plugin = plugin

    def __str__(self) -> str:
        return self.extract()

    def __int__(self):
        return self.to_int(self.extract())

    @property
    def plugin(self):
        return self._plugin

    @classmethod
    def add(cls, versions: List[Union[str, int]]):
        refactored = [cls.to_int(version) if isinstance(version, str) else version for version in versions]

        if refactored:
            versions = refactored

        return sum(versions)

    @classmethod
    def to_int(cls, version: str) -> int:
        pieces = version.split('.')
        result = 0

        try:
            for index, piece in enumerate(pieces):
                result += int(piece) * cls.FACTORS[index]
        except Exception:
            result = 0

        return result

    @classmethod
    def to_str(cls, version: int) -> str:
        if version <= 0:
            exceptions.InvalidArgumentError(f"Version must be greater than 0")


        components = []
        remaining_value = version

        for factor in Version.FACTORS:
            component = remaining_value // factor
            components.append(str(component))

            remaining_value %= factor

        return ".".join(components)

    def extract(self):
        try:
            with open (self._plugin, 'r') as plugin:
                content = plugin.read()
                match = re.search(self.PATTERN, content)

                if match:
                    return match.group(1)
        except IOError as e:
            raise exceptions.BooException(f"An error occurred while reading the '{self._plugin}': {e}")

    def update(self, version: str):
        plugin = file.Plugin(os.path.dirname(self._plugin))

        content = plugin.content()

        content = re.sub(
            Version.PATTERN,
            f"* Version: {version}",
            content
        )

        plugin.update(content)