from tabulate import tabulate
from typing import List, Dict, Tuple, AnyStr
import os
import subprocess
import click

from commands.base_command import BaseCommand
import file
import helpers
import exceptions
import git


class UpgradeCommand(BaseCommand):
    """
    Upgrade tool by checking for new commits in the repository located at /opt/boo.
    If new commits exist, pull them.
    """
    REPO_PATH = "/opt/boo"

    def run(self):
        """
        Executes the upgrade command.
        """
        if not os.path.isdir(self.REPO_PATH):
            raise exceptions.BooException(f"Repository path '{self.REPO_PATH}' does not exist.")

        try:
            click.echo("Checking for updates...")

            # Fetch the latest changes from the remote using the Git module
            git.Git.fetch(self.REPO_PATH)

            # Check if there are new commits in the remote using the Git module
            if git.Git.has_new_commits(self.REPO_PATH):
                click.echo("New updates found! Pulling the latest changes...")
                git.Git.pull(self.REPO_PATH)
                click.echo("Update complete!")
            else:
                click.echo("Already up to date.")

        except subprocess.CalledProcessError as e:
            raise exceptions.BooException(
                f"An error occurred while executing a Git command: {e}\n"
                f"Please make sure you have the necessary permissions to access the repository at '{self.REPO_PATH}'."
            )

        except PermissionError:
            suggested_fix = self.__suggest_permission_fix()
            raise exceptions.BooException(
                f"Permission denied while accessing the repository at '{self.REPO_PATH}'.\n"
                f"Please check the file permissions and try again. {suggested_fix}"
            )

        except Exception as e:
            raise exceptions.BooException(f"An error occurred during the upgrade process: {e}")

    def __suggest_permission_fix(self) -> str:
        """
        Suggests potential fixes for permission issues.

        :return: A string with suggestions for fixing permission issues.
        """
        user = os.getenv("USER", "the current user")
        group = "the appropriate group"

        return (
            f"Did you mean to run the command with elevated privileges? "
            f"Try using 'sudo' before the command if necessary.\n"
            f"Alternatively, you can change the ownership of the repository using:\n"
            f"  sudo chown -R {user}:{group} {self.REPO_PATH}\n"
            f"Or, you can adjust the permissions with:\n"
            f"  sudo chmod -R 755 {self.REPO_PATH}"
        )


class VersionsCommand(BaseCommand):
    def __init__(self, path: str = "./", style: str = "outline"):
        """
        Initializes the VersionsCommand with default path and style.

        :param path: Plugins directory path.
        :param style: Table output style.
        """
        self.path: str = path
        self.style: str = style
        self.table_headers: Tuple[str, str, str] = (
            "Plugin Name",
            "Plugin DN Version",
            "Plugin Version"
        )

    def run(self) -> None:
        """
        Executes the command to display plugin versions.
        """
        output: AnyStr = self.__get_output()
        click.echo(output)

    def __get_output(self) -> AnyStr:
        """
        Generates the output table string.

        :return: Formatted table string.
        """
        data = self.__get_data(file.Plugin.list(self.path))
        return tabulate(data, tablefmt=self.style, headers=self.table_headers)

    def __get_data(self, plugins: list[file.Plugin]) -> object:
        for plugin in plugins:
            yield [
                helpers.stylize(plugin.name),
                helpers.stylize(str(plugin.version)),
                helpers.stylize(int(plugin.version)),
            ]


class UpdateCommand(BaseCommand):
    def __init__(self, plugin_abspath: str = "./", increase: str = "0.0.0", decrease: str = "0.0.0",
                 commit: bool = False, zip: str = "./") -> None:
        self.plugin = file.Plugin(plugin_abspath)
        self.increase: str = increase
        self.decrease: str = decrease
        self.commit: bool = commit
        self.zip: str = zip

    def run(self) -> Dict:
        try:
            current_version = int(self.plugin.version)
            self.decrease = -file.Version.to_int(self.decrease)

            new_version = file.Version.to_str(self.plugin.version.add([
                current_version,
                self.increase,
                self.decrease
            ]))

            data = {
                "plugin_name": self.plugin.name,
                "old_version": file.Version.to_str(current_version),
                "new_version": new_version,
            }

            self.plugin.version.update(new_version)
        except Exception as e:
            raise exceptions.BooException(f"An error occurred while updating the '{self.plugin.name}' version: {e}")

        if self.zip:
            self.__zip()

        if self.commit:
            self.__commit(data)

        return data

    def __zip(self):
        version = int(self.plugin.version)
        plugin = self.plugin.name

        plugin_abspath = self.plugin.full_path
        zip_path = os.path.join(self.zip, f"{plugin}-{version}.zip")

        file.Zip.create(plugin_abspath, zip_path)

    def __commit(self, data: Dict) -> None:
        commit_message = helpers.prepare_update_message(**data)
        helpers.commit([self.plugin.full_path], commit_message)


class MultiUpdateCommand(BaseCommand):
    def __init__(self, plugins_path: str = "./", increase: str = "0.0.0", decrease: str = "0.0.0", include: tuple = (),
                 exclude: tuple = (), style: str = "outline", commit: bool = False, zip: str = "./") -> None:
        self.plugins_path: str = plugins_path
        self.increase: str = increase
        self.decrease: str = decrease
        self.include: tuple = include
        self.exclude: tuple = exclude
        self.style: str = style
        self.commit: bool = commit
        self.zip: str = zip
        self.table_headers = ("Plugin Name", "Info")

    def run(self):
        data = []

        plugins_in_dir = file.Plugin.list(self.plugins_path)
        plugin_abspaths = file.Plugin.filter(
            [plugin.full_path for plugin in plugins_in_dir],
            list(self.include),
            list(self.exclude)
        )

        for plugin_abspath in plugin_abspaths:
            update_command: UpdateCommand = UpdateCommand(
                plugin_abspath=plugin_abspath,
                increase=self.increase,
                decrease=self.decrease,
                zip=self.zip
            )

            updated = update_command.run()

            plugin_name = helpers.stylize(os.path.basename(plugin_abspath))
            data.append((plugin_name, updated))

        table = self.__create_table(data)
        click.echo(table)

        if self.commit:
            self.__commit(plugin_abspaths, data)

    def __commit(self, plugin_abspaths: List, data: List[Tuple[str, dict]]):
        commit_messages = [helpers.prepare_update_message(**updated_info) for plugin_name, updated_info in data]
        helpers.commit(plugin_abspaths, "\n".join(commit_messages))

    def __create_table(self, data: List[Tuple[str, dict]]) -> str:
        table_data = [(plugin_name, helpers.prepare_update_message(**updated_info, color=True))
                      for plugin_name, updated_info in data]

        return tabulate(
            table_data,
            tablefmt=self.style,
            headers=self.table_headers
        )
