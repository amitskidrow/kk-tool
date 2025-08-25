# kk - Namespace-Aware GNOME Keyring CLI

A lightweight, namespace-aware CLI to safely browse and manage secrets in GNOME Keyring (Secret Service), designed for agentic CLI workflows.

## Features

- **Namespaces**: All items are scoped by `kk_ns=<namespace>` (default `ss`).
- **Unified storage**: One storage layer used by CLI and ingestor (Secret Service via DBus).
- **Safe browsing**: `list`/`search` show masked secrets (~35% visible by default).
- **Isolation**: By default only shows items created by `kk` in your namespace.
- **Confirmation required**: Full secret retrieval requires explicit confirmation.
- **Bulk ingestion**: Ingest `.env` files consistently with the same contract.

## Installation

Local development: use `python -m kkcli --version` or `./kk`. Packaging is provided via `pyproject.toml`.

### Requirements

- `python>=3.9`, `secretstorage` Python package
- A running Secret Service (e.g., GNOME Keyring) on DBus

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

# Get full secret (confirm)
kk get binance/USER1

# Set or update a secret
kk set binance/USER1 --value your_secret

# Remove (confirm)
kk remove binance/USER1

# Ingest .env files in a directory
kk ingest credentials/ --env dev --dry-run
```

## For Agentic CLI Tools

The `list` and `search` commands show masked secrets (~35% visible) which allows agents to:
- Verify that secrets exist
- Identify the correct service and username parameters for retrieval
- Work with secrets safely without exposing them

Example masked output:
```
Service              Username             Label                          Secret (masked)
------------------------------------------------------------------------------------------
binance              trader1              Binance API Key                binance-api-k******
```

Only the `get` command shows full secrets, and requires explicit confirmation:
```
Show full secret for 'Binance API Key'? Type 'yes' to confirm:
```

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

## Secret Ingestion Script

A Python script `ingest_secrets.py` is included to bulk import secrets from `.env` files:

```bash
# Ingest via CLI (recommended)
kk ingest . --dry-run

# Legacy wrapper (delegates to kk ingest)
python ingest_secrets.py --dry-run
```

The script follows these conventions:
- Files named `.binance.env` will create secrets with service name "binance"
- Files named `test.env` will create secrets with service name "test"
- Each key-value pair in the file becomes a separate secret
- Keys become the username/label, values become the secret

Example `.binance.env` file:
```
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here
```

This will create two secrets in the `kk` namespace (default `ss`) with label `binance/BINANCE_*`, idempotently.

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

Environment overrides: `KK_NAMESPACE`, `KK_STORE_MODE`, `KK_DEFAULT_ENV`, `KK_MASK_VISIBLE_RATIO`.

## License

MIT
