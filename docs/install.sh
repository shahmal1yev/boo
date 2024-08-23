#!/bin/bash

# Function to check if the script is run as root
check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        echo "[boo]: This script must be run as root. Use 'sudo' to run it."
        exit 1
    fi
}

# Check if the script is run as root
check_root

# Get the original user who invoked sudo
ORIGINAL_USER=$(logname)

# Define the repository path and installation path
REPO_PATH="/home/$ORIGINAL_USER/boo"
SYMLINK_PATH="/usr/local/bin/boo"

# Get the default shell of the original user
USER_SHELL=$(getent passwd "$ORIGINAL_USER" | cut -d: -f7)

# Clone the repository if it doesn't exist
if [ ! -d "$REPO_PATH" ]; then
    echo "[boo]: Cloning repository into $REPO_PATH"
    sudo -u "$ORIGINAL_USER" git clone https://github.com/shahmal1yev/boo "$REPO_PATH"
else
    echo "[boo]: Directory $REPO_PATH already exists. Skipping clone."
fi

echo
# Create virtual environment if it doesn't exist
echo "[boo]: Creating virtual environment"
if [ ! -d "$REPO_PATH/.venv" ]; then
    sudo -u "$ORIGINAL_USER" python3 -m venv "$REPO_PATH/.venv"
else
    echo "[boo]: Virtual environment already exists at $REPO_PATH/.venv"
fi

run_in_virtual_env() {
    local command="$1"
    sudo -u "$ORIGINAL_USER" -H bash -c "source $REPO_PATH/.venv/bin/activate && $command"
}

# Validate if the virtual environment is activated
validate_venv() {
    local result
    result=$(run_in_virtual_env '[[ -n "$VIRTUAL_ENV" ]] && echo "1" || echo "0"')
    if [ "$result" -eq 1 ]; then
        echo "Virtual environment is activated"
        return 0
    else
        echo "Virtual environment is not activated"
        return 1
    fi
}

# Example usage
validate_venv
if [ $? -ne 0 ]; then
    echo "Exiting because virtual environment is not activated."
    exit 1
fi

echo
echo "[boo]: Activating virtual environment and installing dependencies"
# Install dependencies
run_in_virtual_env "pip install -r $REPO_PATH/requirements.txt"

echo
echo "[boo]: Running tests"
# Run tests
run_in_virtual_env "python3 -m unittest discover -s '$REPO_PATH' -v"

echo
# Create symbolic link if it doesn't exist
if [ ! -L "$SYMLINK_PATH" ]; then
    echo "[boo]: Creating symbolic link to $REPO_PATH/main"
    ln -s "$REPO_PATH/main" "$SYMLINK_PATH"
    echo "[boo]: Symbolic link created: $SYMLINK_PATH -> $REPO_PATH/main"
else
    echo "[boo]: Symbolic link $SYMLINK_PATH already exists. Skipping creation."
fi

# Function to add the check-updates function to the user's profile file
add_check_update_to_profile() {
    local profile_file

    case "$USER_SHELL" in
        */zsh)
            profile_file="/home/$ORIGINAL_USER/.zshrc"
            ;;
        */bash)
            profile_file="/home/$ORIGINAL_USER/.bashrc"
            ;;
        *)
            # Default to bash if no specific shell detected
            profile_file="/home/$ORIGINAL_USER/.bashrc"
            ;;
    esac

    if ! grep -q "boo_check_update" "$profile_file"; then
        echo "[boo]: Adding check-updates command to $profile_file"
        cat >> "$profile_file" <<EOF

# Function to check for updates to Boo CLI tool on every new shell session
boo_check_update() {
    if [ -x "$SYMLINK_PATH" ]; then
        boo check-updates
    fi
}

boo_check_update
EOF
        echo "[boo]: check-updates command added to $profile_file"
    else
        echo "[boo]: check-updates command already exists in $profile_file. Skipping addition."
    fi
}

# Add the check-updates function to the original user's profile
add_check_update_to_profile

echo
echo "[boo]: Installation completed successfully. Test it with 'boo'"
