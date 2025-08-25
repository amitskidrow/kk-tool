# kk - GNOME Keyring Browser

A lightweight CLI tool to safely browse and manage secrets in GNOME Keyring, designed specifically for agentic CLI workflows.

## Features

- **Safe secret browsing**: List and search commands show masked secrets (70% visible) to prevent accidental exposure
- **Agent-friendly**: Allows agents to verify secrets exist and identify parameters without exposing full secrets
- **Simple installation**: One-liner global installation via curl
- **Standard GNOME Keyring integration**: Uses `secret-tool` under the hood
- **Confirmation required**: Full secret retrieval requires explicit user confirmation
- **Secret management**: Remove secrets with confirmation to prevent accidental deletion
- **Bulk ingestion**: Python script to ingest secrets from .env files

## Installation

Install globally with a single command:

```bash
curl -sSL https://raw.githubusercontent.com/amitskidrow/kk-tool/main/install.sh | bash
```

This will:
1. Check for required dependencies
2. Download the latest version of `kk`
3. Install it to `/usr/local/bin` (system-wide) or `~/.local/bin` (user-only)
4. Make it executable and available in your PATH

### Requirements

- `secret-tool` (usually part of `libsecret-tools` package)
- `curl` or `wget` for downloading

## Usage

```bash
# Show help
kk --help

# Show version
kk --version

# List all secrets (masked)
kk list

# Search for secrets by attribute (masked)
kk search service binance

# Get full secret (requires confirmation)
kk get binance trader1

# Remove a secret (requires confirmation)
kk remove binance trader1
```

## For Agentic CLI Tools

The `list` and `search` commands show masked secrets (first 70% visible) which allows agents to:
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

While `kk` is a CLI tool, you can also access GNOME Keyring secrets directly in Python using the `keyring` library, which is the underlying library that `kk` uses for secret management.

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
# Run in dry-run mode to see what would be imported
python ingest_secrets.py --dry-run

# Actually import secrets
python ingest_secrets.py
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

This will create two secrets in the keyring with service name "binance", usernames "BINANCE_API_KEY" and "BINANCE_SECRET_KEY", and the corresponding values as secrets.

## License

MIT