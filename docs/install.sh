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

echo
# Activate virtual environment and install dependencies
echo "[boo]: Installing dependencies"
source "$REPO_PATH/.venv/bin/activate"
sudo -u "$ORIGINAL_USER" pip install -r "$REPO_PATH/requirements.txt"

echo
# Run tests
echo "[boo]: Running tests"
sudo -u "$ORIGINAL_USER" python3 -m unittest discover -s "$REPO_PATH" -v

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

# Deactivate virtual environment
deactivate

echo
echo "[boo]: Installation completed successfully. Test it with 'boo'"
