# kk - Namespace-Aware GNOME Keyring CLI

A lightweight, namespace-aware CLI to safely browse and manage secrets in GNOME Keyring (Secret Service), designed for agentic CLI workflows.

## Features

- **Fixed context**: Namespace is always `ss` and environment tag is always `dev`, keeping agent workflows predictable.
- **Unified storage**: One storage layer used by CLI and ingestor (Secret Service via DBus).
- **Safe browsing**: `list`/`search` show masked secrets (~35% visible by default) with optional JSON output for agents.
- **Controlled retrieval**: `get` masks by default and reveals the full secret only when invoked with `--pass ss`.
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

# List as JSON for automations
kk list --json

# Search (masked)
kk search binance

# Get masked secret (default)
kk get binance/USER1

# Reveal full secret with passphrase
kk get binance/USER1 --pass ss

# Set or update a secret
kk set binance/USER1 --value your_secret

# Preview set without writing (also works with --json)
kk set binance/USER1 --value your_secret --dry-run

# Remove
kk remove binance/USER1 --no-confirm

# Dry run removal
kk remove binance/USER1 --dry-run

# Ingest dot-env files (.*.env) recursively from a directory
kk ingest credentials/

# Optional: preview without writing
kk ingest credentials/ --dry-run

# Ingest a single .env file
kk ingest CREDENTIALS/.binance.env

# Clean the namespace (destructive; requires explicit yes)
kk clean yes

# Preview what clean would delete
kk clean --dry-run

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
- Secrets are always tagged with environment `dev`.

## Fixed Context

`kk` is intentionally opinionated so agents never have to manage configuration:

- Namespace is hard-coded to `ss`.
- Environment metadata is always set to `dev`.
- Store mode defaults to Secret Service attribute filtering.

Older configuration files and environment variables are ignored; the CLI prints the active context (`ns=ss, mode=attribute, env=dev`) at runtime for clarity.

## License

MIT
Automation tips:
- Append `--json` to `list`, `search`, `get`, `set`, and `remove` for machine-friendly responses (context + result payloads).
- Use `--dry-run` with mutating commands (`set`, `remove`, `clean`, `ingest`) to preview actions before writing secrets.
