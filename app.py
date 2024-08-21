import click
from typing import Dict

import commands


class Boo:
    __commands: Dict[str, str] = {
        'versions': 'versions',
        'update': 'update',
        'multi-update': 'multi-update',
    }

    @classmethod
    def run(cls):
        cls.__register()
        cls.__tool()

    @classmethod
    def __register(cls):
        cls.__tool.add_command(cls.versions)
        cls.__tool.add_command(cls.update)
        cls.__tool.add_command(cls.multi_update)

    @staticmethod
    @click.group()
    def __tool():
        pass

    @staticmethod
    @click.command(__commands['versions'])
    @click.option('--path', default="./", help='Plugins directory path. Default: ./')
    @click.option('--style', default="outline", help="Set tabulate output style. Default: outline")
    def versions(path, style):
        command: commands.VersionsCommand = commands.VersionsCommand(path=path, style=style)
        command.run()

    @staticmethod
    @click.command(__commands['update'])
    @click.option("-p", "--path", "plugin_absolute_path", default="./", help="Plugins directory path. Default: ./")
    @click.option("-i", "--increase", "increase", default="0.0.0", help="Increase version of plugins.")
    @click.option("-d", "--decrease", "decrease", default="0.0.0", help="Decrease version of plugins.")
    @click.option("-c", "--commit", is_flag=True, help="Commit changes to Git after updating.")
    @click.option("-z", "--zip", type=str, help="Path to save the zip files of updated plugins.")
    def update(plugin_absolute_path, increase, decrease, commit, zip):
        command: commands.UpdateCommand = commands.UpdateCommand(plugin_absolute_path, increase, decrease, commit, zip)
        command.run()

    @staticmethod
    @click.command(__commands['multi-update'])
    @click.option("-p", "--path", "plugins_path", default="./", help="Plugins directory path. Default: ./")
    @click.option("-i", "--increase", "increase", default="0.0.0", help="Increase version of plugins.")
    @click.option("-d", "--decrease", "decrease", default="0.0.0", help="Decrease version of plugins.")
    @click.option("-i", "--include", "include", multiple=True, help="Include version of plugins.")
    @click.option("-e", "--exclude", "exclude", multiple=True, help="Exclude version of plugins.")
    @click.option("-s", "--style", "style", default="outline", help="Set tabulate output style.")
    @click.option("-c", "--commit", is_flag=True, help="Commit changes to Git after updating.")
    @click.option("-z", "--zip", type=str, help="Path to save the zip files of updated plugins.")
    def multi_update(plugins_path, increase, decrease, include, exclude, style, commit, zip):
        print(commit)
        command: commands.MultiUpdateCommand = commands.MultiUpdateCommand(
            plugins_path,
            increase,
            decrease,
            include,
            exclude,
            style,
            commit,
            zip
        )
        command.run()
