#!/bin/bash

# secret-browser install script
# Usage: curl -sSL https://raw.githubusercontent.com/amitskidrow/kk-tool/main/install.sh | bash

set -e

echo "Installing secret-browser..."

# Check if pipx is installed
if ! command -v pipx &> /dev/null; then
    echo "pipx is not installed. Installing pipx first..."
    
    # Check if we're on Ubuntu/Debian
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y pipx
    # Check if we're on Fedora
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y pipx
    # Check if we're on Arch Linux
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm pipx
    else
        # Fallback: install pipx using pip
        python3 -m pip install --user pipx
    fi
    
    # Ensure pipx is in PATH
    python3 -m pipx ensurepath
fi

# Install secret-browser from the GitHub repository
echo "Installing secret-browser from GitHub repository..."
pipx install git+https://github.com/amitskidrow/kk-tool.git

echo "Installation complete!"
echo "You can now use the 'secret-browser' command:"
echo "  secret-browser list              # List all secrets (masked)"
echo "  secret-browser search <attr> <value>  # Search for secrets"
echo "  secret-browser get <service> <username>  # Get full secret"

# Check if we need to restart shell or source a file
if ! command -v secret-browser &> /dev/null; then
    echo ""
    echo "The secret-browser command is not available in your current shell."
    echo "Please restart your terminal or run one of the following commands:"
    
    # Check for common shell config files
    if [ -f "$HOME/.bashrc" ]; then
        echo "  source ~/.bashrc"
    fi
    
    if [ -f "$HOME/.zshrc" ]; then
        echo "  source ~/.zshrc"
    fi
    
    if [ -f "$HOME/.profile" ]; then
        echo "  source ~/.profile"
    fi
fi