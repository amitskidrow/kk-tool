# Secret Browser

A CLI tool to browse and manage secrets in GNOME Keyring, designed for both human users and agentic CLI tools.

## Features

- **Safe for agentic CLIs**: List and search commands show masked secrets (first 70% visible, rest hidden)
- **Human-friendly**: Get command retrieves full secrets with confirmation prompt
- **Minimal and secure**: No unnecessary dependencies or boilerplate code
- **Linux-only**: Designed specifically for Linux systems with GNOME Keyring

## Installation

### Using pipx (recommended)

```bash
pipx install git+https://github.com/yourusername/secret-browser.git
```

### Using pip

```bash
pip install git+https://github.com/yourusername/secret-browser.git
```

## Usage

### List all secrets (masked)
```bash
secret-browser list
```

### Search for secrets by attribute (masked)
```bash
secret-browser search service binance
```

### Retrieve a full secret (with confirmation)
```bash
secret-browser get binance trader1
```

### Show full secrets (WARNING: Exposes sensitive data)
```bash
secret-browser list --unmask
secret-browser search service binance --unmask
```

## Commands

| Command | Description |
|---------|-------------|
| `list` | List all secrets (with masked values by default) |
| `search` | Search for secrets by attribute |
| `get` | Retrieve a full secret (requires confirmation) |
| `version` | Show version |

## For Agentic CLI Tools

When using with agentic CLI tools like Claude Code or Qwen Code, use the `list` or `search` commands which show masked secrets. This allows the agent to:

1. Verify that a secret exists
2. Identify the service and username
3. Know what parameters to use with the `get` command

The masking shows the first 70% of the secret, which is enough for identification without exposing the full secret.