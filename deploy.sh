#!/usr/bin/env bash
set -euo pipefail

# Get current timestamp
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Add and commit all changes with timestamp
git add .
git commit -m "Auto deploy: $TIMESTAMP"
echo "Committed changes with timestamp: $TIMESTAMP"

# Push to GitHub
git push origin main
echo "Pushed to GitHub"

# Wait a bit for GitHub's cache to update
echo "Waiting for GitHub cache to update..."
sleep 15

# Install via curl and log version
echo "Installing via curl..."
INSTALL_OUTPUT=$(curl -sSL https://raw.githubusercontent.com/amitskidrow/kk-tool/main/install.sh | bash)
echo "$INSTALL_OUTPUT"

# Extract version from the installation output
if echo "$INSTALL_OUTPUT" | grep -q "Installation completed successfully"; then
    echo "Installation successful"
else
    echo "Installation failed"
    echo "$INSTALL_OUTPUT"
    exit 1
fi

# Test the installed version directly
echo "Testing installed version..."
if command -v kk >/dev/null 2>&1; then
    INSTALLED_VERSION=$(kk --version 2>/dev/null || echo "Failed to get version")
    echo "Installed version: $INSTALLED_VERSION"
    
    # Test list command
    echo "Testing kk list command..."
    LIST_OUTPUT=$(kk list 2>/dev/null || echo "Failed to run list command")
    echo "List command output:"
    echo "$LIST_OUTPUT"
    
    # Test search command
    echo "Testing kk search command..."
    SEARCH_OUTPUT=$(kk search service test-service 2>/dev/null || echo "Failed to run search command")
    echo "Search command output:"
    echo "$SEARCH_OUTPUT"
else
    echo "kk command not found in PATH"
    exit 1
fi