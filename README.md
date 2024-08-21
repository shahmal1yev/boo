# Boo Command Line Tool

![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/shahmal1yev/boo?label=latest&style=flat)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
![GitHub last commit](https://img.shields.io/github/last-commit/shahmal1yev/boo)
![GitHub issues](https://img.shields.io/github/issues/shahmal1yev/boo)
![GitHub stars](https://img.shields.io/github/stars/shahmal1yev/boo)
![GitHub forks](https://img.shields.io/github/forks/shahmal1yev/boo)
![GitHub contributors](https://img.shields.io/github/contributors/shahmal1yev/boo)

`boo` is a command-line interface (CLI) tool built with Python's `click` library. It provides commands to manage versions of wordpress plugins, update them, and handle multiple updates efficiently.

## Installation

To install the required dependencies for this tool, use the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Usage

This CLI tool provides the following commands:

### 1. `versions`

Displays the versions of plugins in a specified directory.

**Usage:**

```bash
python your_script.py versions --path=<path_to_plugins_directory> --style=<output_style>
```

**Options:**

- `--path` (default: `./`): Plugins directory path.
- `--style` (default: `outline`): Set tabulate output style.

### 2. `update`

Updates the version of a specific plugin in a specified directory.

**Usage:**

```bash
python your_script.py update --path=<plugin_directory_path> --increase=<version_increase> --decrease=<version_decrease> [--commit] [--zip=<zip_path>]
```

**Options:**

- `--path` (default: `./`): Plugin directory path.
- `--increase` (default: `0.0.0`): Increase version of plugins.
- `--decrease` (default: `0.0.0`): Decrease version of plugins.
- `--commit`: Commit changes to Git after updating.
- `--zip`: Path to save the zip files of updated plugins.

### 3. `multi-update`

Performs batch updates on multiple plugins in a specified directory.

**Usage:**

```bash
python your_script.py multi-update --path=<plugins_directory_path> --increase=<version_increase> --decrease=<version_decrease> [--include=<plugins_to_include>] [--exclude=<plugins_to_exclude>] [--style=<output_style>] [--commit] [--zip=<zip_path>]
```

**Options:**

- `--path` (default: `./`): Plugins directory path.
- `--increase` (default: `0.0.0`): Increase version of plugins.
- `--decrease` (default: `0.0.0`): Decrease version of plugins.
- `--include`: Include specific plugins for updating.
- `--exclude`: Exclude specific plugins from updating.
- `--style` (default: `outline`): Set tabulate output style.
- `--commit`: Commit changes to Git after updating.
- `--zip`: Path to save the zip files of updated plugins.

## How to Run

To run any of the commands, use the following syntax:

```bash
python your_script.py <command> [OPTIONS]
```

Replace `<command>` with one of the available commands (`versions`, `update`, `multi-update`), and `[OPTIONS]` with the appropriate options for that command.

## Example

```bash
python your_script.py versions --path="./plugins" --style="outline"
```

This command will list the versions of all plugins in the `./plugins` directory using the `outline` style.

```bash
python your_script.py update --path="./plugin" --increase="1.0.1" --commit
```

This command will update the version of a plugin in the `./plugin` directory to `1.0.1` and commit the changes to Git.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Notes:

1. Replace `your_script.py` with the actual name of your Python script that contains the `boo` class.
2. Add any additional instructions or examples as needed based on your specific use case or setup.