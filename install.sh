#!/bin/bash

# Installation script for kk - A CLI tool to browse and manage secrets in GNOME Keyring
# Usage: curl -sSL https://raw.githubusercontent.com/amitskidrow/kk-tool/main/install.sh | bash

set -e

# Define variables
REPO_URL="https://raw.githubusercontent.com/amitskidrow/kk-tool/main"
INSTALL_DIR="/usr/local/bin"
USER_INSTALL_DIR="$HOME/.local/bin"
TOOL_NAME="kk"
TEMP_DIR=$(mktemp -d)

# Cleanup function
cleanup() {
    rm -rf "$TEMP_DIR"
}

# Trap exit to cleanup
trap cleanup EXIT

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if we can write to a directory
can_write_to_dir() {
    touch "$1/.kk_test" 2>/dev/null && rm -f "$1/.kk_test"
}

# Function to print error message
print_error() {
    echo "Error: $1" >&2
}

# Function to print info message
print_info() {
    echo "INFO: $1"
}

# Function to check dependencies
check_dependencies() {
    print_info "Checking dependencies..."
    
    # Check if secret-tool is installed
    if ! command_exists secret-tool; then
        print_error "secret-tool is not installed. Please install libsecret-tools package."
        exit 1
    fi
    
    # Check if curl or wget is installed
    if ! command_exists curl && ! command_exists wget; then
        print_error "Either curl or wget is required for installation."
        exit 1
    fi
    
    print_info "All dependencies are satisfied."
}

# Function to download file
download_file() {
    local url="$1"
    local dest="$2"
    
    if command_exists curl; then
        curl -sSL "$url" -o "$dest"
    elif command_exists wget; then
        wget -qO "$dest" "$url"
    else
        print_error "No download tool available"
        exit 1
    fi
}

# Function to install the tool
install_tool() {
    print_info "Downloading $TOOL_NAME..."
    
    # Download the tool
    download_file "$REPO_URL/$TOOL_NAME" "$TEMP_DIR/$TOOL_NAME"
    
    # Check if download was successful
    if [ ! -f "$TEMP_DIR/$TOOL_NAME" ]; then
        print_error "Failed to download $TOOL_NAME"
        exit 1
    fi
    
    # Make it executable
    chmod +x "$TEMP_DIR/$TOOL_NAME"
    
    # Try to install to system directory first
    if can_write_to_dir "$INSTALL_DIR"; then
        sudo cp "$TEMP_DIR/$TOOL_NAME" "$INSTALL_DIR/"
        print_info "$TOOL_NAME has been installed to $INSTALL_DIR/$TOOL_NAME"
        INSTALL_PATH="$INSTALL_DIR/$TOOL_NAME"
    # If that fails, try user directory
    elif can_write_to_dir "$USER_INSTALL_DIR"; then
        mkdir -p "$USER_INSTALL_DIR"
        cp "$TEMP_DIR/$TOOL_NAME" "$USER_INSTALL_DIR/"
        print_info "$TOOL_NAME has been installed to $USER_INSTALL_DIR/$TOOL_NAME"
        INSTALL_PATH="$USER_INSTALL_DIR/$TOOL_NAME"
    else
        print_error "Cannot write to $INSTALL_DIR or $USER_INSTALL_DIR"
        exit 1
    fi
    
    # Verify installation
    if [ -f "$INSTALL_PATH" ]; then
        print_info "Installation successful!"
        echo ""
        echo "You can now use the $TOOL_NAME command:"
        echo "  $TOOL_NAME --help     # Show help"
        echo "  $TOOL_NAME --version  # Show version"
        echo "  $TOOL_NAME list       # List all secrets (masked)"
        echo "  $TOOL_NAME search <attribute> <value>  # Search for secrets"
        echo "  $TOOL_NAME get <service> <username>    # Get full secret"
        echo ""
        echo "For agentic CLI tools:"
        echo "  The list and search commands show masked secrets (first 70% visible)"
        echo "  This allows agents to verify secrets exist and identify parameters for get"
        echo ""
        
        # Check if the tool is in PATH
        if ! command -v "$TOOL_NAME" >/dev/null 2>&1; then
            echo "NOTE: $TOOL_NAME is not in your PATH."
            if [ "$INSTALL_PATH" = "$USER_INSTALL_DIR/$TOOL_NAME" ]; then
                echo "Please add $USER_INSTALL_DIR to your PATH by adding this line to your shell configuration file:"
                echo "  export PATH=\"\$PATH:$USER_INSTALL_DIR\""
                echo "Then restart your terminal or run: source ~/.bashrc (or ~/.zshrc)"
            fi
        fi
    else
        print_error "Installation failed"
        exit 1
    fi
}

# Main function
main() {
    echo "Installing $TOOL_NAME..."
    
    # Check dependencies
    check_dependencies
    
    # Install the tool
    install_tool
    
    echo "Installation completed successfully!"
}

# Run main function
main "$@"