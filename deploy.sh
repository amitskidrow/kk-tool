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

# Install via curl
echo "Installing via curl..."
curl -sSL https://raw.githubusercontent.com/amitskidrow/kk-tool/main/install.sh | bash
echo "Installation attempted"

# Validate kk is available and print version
echo "Testing installed version..."
if command -v kk >/dev/null 2>&1; then
    set +e
    kk --version
    VERSION_STATUS=$?
    echo "Running kk doctor (non-fatal)..."
    kk doctor || true
    set -e
    if [ "$VERSION_STATUS" -ne 0 ]; then
        echo "kk --version failed"
        exit 1
    fi
else
    echo "kk command not found in PATH"
    exit 1
fi
