#!/usr/bin/env bash
set -euo pipefail

# Installation script for kk via Python package (kktool)
# Usage: curl -sSL https://raw.githubusercontent.com/amitskidrow/kk-tool/main/install.sh | bash

PKG_NAME="kktool"
REPO_REF="git+https://github.com/amitskidrow/kk-tool@main"
BINARY_NAME="kk"
USER_BIN="$HOME/.local/bin"

info() { echo "INFO: $*"; }
warn() { echo "WARN: $*" >&2; }
err()  { echo "ERROR: $*" >&2; }

have() { command -v "$1" >/dev/null 2>&1; }

ensure_python() {
  if ! have python3; then
    err "python3 not found. Please install Python 3.9+ and re-run."
    exit 1
  fi
}

install_with_pipx() {
  info "Installing with pipx (force upgrade)..."
  pipx install --force "$REPO_REF"
}

install_with_pip_user() {
  info "Installing with pip --user (upgrade)..."
  if ! have pip3 && ! python3 -m pip --version >/dev/null 2>&1; then
    err "pip not found for python3. Please install pip or pipx."
    exit 1
  fi
  python3 -m pip install --user --upgrade "$REPO_REF"
}

print_path_hint() {
  if ! echo ":$PATH:" | grep -q ":$USER_BIN:"; then
    warn "$USER_BIN is not in your PATH. Add it with:"
    echo "  export PATH=\"\$PATH:$USER_BIN\""
    echo "Then restart your shell or source your rc file."
  fi
}

post_install_check() {
  hash -r || true
  local kk_path
  if have "$BINARY_NAME"; then
    kk_path=$(command -v "$BINARY_NAME")
  elif [ -x "$USER_BIN/$BINARY_NAME" ]; then
    kk_path="$USER_BIN/$BINARY_NAME"
  else
    kk_path=""
  fi

  if [ -z "$kk_path" ]; then
    err "Installation appears to have succeeded but '$BINARY_NAME' not found on PATH."
    print_path_hint
    return 1
  fi

  info "Installed to: $kk_path"
  echo ""
  echo "Smoke test:"
  set +e
  "$kk_path" --version
  "$kk_path" doctor || true
  set -e

  echo ""
  echo "Next steps:"
  echo "  kk --help     # Show help"
  echo "  kk list       # List secrets (masked)"
  echo "  kk get <service> <username>  # Show full secret"

  print_path_hint
}

main() {
  info "Installing $BINARY_NAME..."
  ensure_python

  if have pipx; then
    install_with_pipx
  else
    warn "pipx not found; falling back to user-level pip install"
    install_with_pip_user
  fi

  info "Installation successful!"
  post_install_check || true
}

main "$@"
