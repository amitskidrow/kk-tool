# kk - Namespace-Aware GNOME Keyring CLI

A lightweight, namespace-aware CLI to safely browse and manage secrets in GNOME Keyring (Secret Service), designed for agentic CLI workflows.

## Features

- **Fixed context**: Namespace is always `ss` and environment tag is always `dev`, keeping agent workflows predictable.
- **Unified storage**: One storage layer used by CLI and ingestor (Secret Service via DBus).
- **Safe browsing**: `list`/`search` show masked secrets (~35% visible by default) with optional JSON output for agents; automation must never scrape these masked values.
- **Controlled retrieval**: `get` masks by default while keeping plaintext access available for trusted operators.
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

### New: `kk code <selector>`

Return a short description and a ready-to-paste Python snippet that uses **python-keyring** to fetch the credential(s) selected by index (from `kk list`) or by explicit label `service/username`.

Examples:

```bash
kk list
kk code 1
kk code anthropic/ANTHROPIC_API_KEY
kk code 3,4 --json
kk code nats/NATS_URL --quiet
kk code redis/REDIS_URL --emit-markers
```



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

`kk list` and `kk search` deliberately present masked secrets (~35% visible) so humans can confirm that credentials exist without exposing full values.

**Automation guardrails**
- Call the Secret Service via a keyring client (e.g. `python -m keyring get <service> <username>`) to retrieve secrets.
- Do not spawn `kk list` (or any other kk command) inside automation to scrape masked output—the masks exist to prevent leaks to LLM prompts.
- When a secret is fetched via the keyring, keep it in-memory for the shortest time possible and never log, print, or otherwise display the plaintext.
- Reserve `kk get` for trusted human operators; agentic tooling should rely on the keyring API path instead.

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
# Use the secret in-memory without logging or printing it
# e.g., pass it straight into an SDK client initialiser.

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


def configure_client(service: str, username: str, password: str) -> None:
    """Placeholder for your own client initialisation code."""
    # e.g. client.configure(auth_token=password)
    ...


for service, username in services:
    password = keyring.get_password(service, username)
    if password is None:
        continue
    # Hand off the secret to whatever SDK requires it without printing/logging
    configure_client(service, username, password)
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
