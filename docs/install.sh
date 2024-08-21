#!/bin/bash

# Function to check if the script is run as root
check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        echo "This script must be run as root. Use 'sudo' to run it."
        exit 1
    fi
}

# Check if the script is run as root
check_root

# Define the repository path
BOO_REPO_PATH="/opt/boo"

# Clone the repository if it doesn't exist
if [ ! -d "$BOO_REPO_PATH" ]; then
    echo
    echo "Cloning repository into $BOO_REPO_PATH"
    git clone https://github.com/shahmal1yev/boo "$BOO_REPO_PATH"
else
    echo
    echo "Directory $BOO_REPO_PATH already exists. Skipping clone."
fi

echo
# Create virtual environment if it doesn't exist
echo "Creating virtual environment"
if [ ! -d "$BOO_REPO_PATH/.venv" ]; then
    python -m venv "$BOO_REPO_PATH/.venv"
else
    echo
    echo "Virtual environment already exists at $BOO_REPO_PATH/.venv."
fi

echo
# Activate virtual environment and install dependencies
echo "Installing dependencies"
source "$BOO_REPO_PATH/.venv/bin/activate"
pip install -r "$BOO_REPO_PATH/requirements.txt"

echo
# Run tests
echo "Running tests"
python -m unittest discover -s "$BOO_REPO_PATH" -v

echo
# Create a symbolic link if it doesn't exist
if [ ! -L "/usr/local/bin/boo" ]; then
    echo "Creating symbolic link to $BOO_REPO_PATH/main"
    ln -s "$BOO_REPO_PATH/main" /usr/local/bin/boo
    echo "Symbolic link created: /usr/local/bin/boo -> $BOO_REPO_PATH/main"
else
    echo "Symbolic link /usr/local/bin/boo already exists. Skipping creation."
fi

# Deactivate virtual environment
deactivate

echo
echo "Installation completed successfully. Test it with 'boo'"
