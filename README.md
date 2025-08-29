# kk - Namespace-Aware GNOME Keyring CLI

A lightweight, namespace-aware CLI to safely browse and manage secrets in GNOME Keyring (Secret Service), designed for agentic CLI workflows.

## Features

- **Namespaces**: All items are scoped by `kk_ns=<namespace>` (default `ss`).
- **Unified storage**: One storage layer used by CLI and ingestor (Secret Service via DBus).
- **Safe browsing**: `list`/`search` show masked secrets (~35% visible by default).
- **Isolation**: By default only shows items created by `kk` in your namespace.
- **Direct retrieval**: `get` prints the full secret (no extra confirmation).
- **Bulk ingestion**: Ingest dot-env files (`.<name>.env`) recursively from a directory; also supports a single `.env` file path.

## Installation

Quick install with pipx (recommended):

```
pipx install --force git+https://github.com/amitskidrow/kk-tool@main
```

Alternative via installer script:

```
curl -sSL https://raw.githubusercontent.com/amitskidrow/kk-tool/main/install.sh | bash
```

Local development: you can also run from the repo with `./kk`.

### Requirements

- `python>=3.9`; install via `pipx` or `pip`
- Secret Service on DBus (e.g., GNOME Keyring). `kk doctor` reports status.

## Usage

```bash
# Show help
kk --help

# Show version
kk --version

# Show effective context
kk list

# Search (masked)
kk search binance

# Get full secret
kk get binance/USER1

# Set or update a secret
kk set binance/USER1 --value your_secret

# Remove
kk remove binance/USER1

# Ingest dot-env files (.*.env) recursively from a directory
kk ingest credentials/

# Optional: preview without writing
kk ingest credentials/ --dry-run

# Ingest a single .env file
kk ingest CREDENTIALS/.binance.env

# Clean the namespace/env (destructive; requires explicit yes)
kk clean yes

```

## Deploy

After changes, deploy and validate installation flow:

```
./deploy.sh
```

This script commits and pushes, installs via the online installer, then verifies:
- `kk --version` (must succeed)
- `kk doctor` (diagnostics; non-fatal if DBus/keyring is locked/unavailable)
```

## For Agentic CLI Tools

The `list` and `search` commands show masked secrets (~35% visible) which allows agents to:
- Verify that secrets exist
- Identify the correct service and username parameters for retrieval
- Work with secrets safely without exposing them

Example masked output:
```
Name                                     Secret (masked)
--------------------------------------------------------
binance/BINANCE_API_KEY                  binance-api-k******
```

The `get` command prints full secrets directly; use it deliberately.

## Using in Python Scripts

While `kk` is a CLI tool, you can also access GNOME Keyring secrets directly in Python using the `secretstorage`/`keyring` libraries. `kk` talks to Secret Service via `secretstorage`.

First, install the keyring library:
```bash
pip install keyring
```

Then use it in your Python scripts:
```python
import keyring

# Retrieve a secret
password = keyring.get_password('service_name', 'username')
print(f"Retrieved password: {password}")

# Set a secret
keyring.set_password('service_name', 'username', 'new_password')
```

Example script to retrieve broker secrets:
```python
import keyring

services = [
    ('binance', 'trader1'),
    ('upstox', 'investor2'),
    ('coinbase', 'crypto_user3')
]

for service, username in services:
    password = keyring.get_password(service, username)
    print(f"{service}: {password}")
```

The `kk` tool complements Python scripts by providing a safe way to browse and verify secrets from the command line without exposing them.

## Ingestion Conventions

- Directory scan considers only files using the dot-notation pattern: `.<name>.env` (e.g., `.binance.env`).
- Single-file mode accepts any `*.env` file path (e.g., `.binance.env` or `binance.env`).
- The `<name>` prefix becomes the service name (`binance`).
- Each `KEY=VALUE` pair becomes a separate item with label `<service>/<KEY>`.
- The effective env tag is global (see config below) and not set per command.

## Namespaces and Store Modes

- Default namespace is `ss`. Override with `--ns` or `KK_NAMESPACE` env var.
- Default store mode is `attribute` (filters by `kk_ns` in the default collection).
- Optional store mode `collection` uses a dedicated collection `kk:<namespace>` for hard isolation (may prompt to unlock/create).

Config file: `~/.config/kk/config.toml` (values under `[kk]`)
```
[kk]
namespace = "ss"
store_mode = "attribute"  # or "collection"
default_env = "dev"
mask_visible_ratio = 0.35
```

Environment overrides (global): `KK_NAMESPACE`, `KK_STORE_MODE`, `KK_DEFAULT_ENV`, `KK_MASK_VISIBLE_RATIO`.

Env scoping in commands:
- `list`, `search`, `export`, `clean` use the configured `default_env` by default.
- Override with `--env <name>` or show all envs with `--all-envs`.

## License

MIT
