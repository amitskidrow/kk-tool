# kk Tool Test Script

This guide demonstrates core `kk` functionality and ingestion flows.

## Prerequisites

1. GNOME Keyring / Secret Service available (desktop session)
2. `python3` and `secretstorage` installed (installed via `pipx` in normal usage)

## Test Steps

1. Show current secrets (masked):
   ```bash
   ./kk list
   ```

2. Ingest .env files from a directory (dry-run first):
   ```bash
   ./kk ingest CREDENTIALS/ --dry-run
   ```

3. Import for real:
   ```bash
   ./kk ingest CREDENTIALS/
   ```

4. Ingest a single .env file:
   ```bash
   ./kk ingest CREDENTIALS/.binance.env
   ```

5. List again and verify entries:
   ```bash
   ./kk list
   ```

6. Search for a service:
   ```bash
   ./kk search binance
   ```

7. Retrieve a full secret:
   ```bash
   ./kk get binance/BINANCE_API_KEY
   ```

8. Remove a secret (with confirmation prompt unless `--no-confirm` used):
   ```bash
   ./kk remove binance/BINANCE_API_KEY
   ```

9. Verify the secret was removed:
   ```bash
   ./kk search binance
   ```
