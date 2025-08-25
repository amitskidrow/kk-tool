# kk Tool Test Script

This script demonstrates the functionality of the kk tool and the ingestion script.

## Prerequisites

1. GNOME Keyring must be running
2. secret-tool must be installed
3. Python keyring library must be installed

## Test Steps

1. First, let's see what secrets we currently have:
   ```bash
   ./kk list
   ```

2. Run the ingestion script in dry-run mode to see what would be imported:
   ```bash
   ./ingest_secrets.py --dry-run
   ```

3. Actually import the secrets:
   ```bash
   ./ingest_secrets.py
   ```

4. List the secrets again to see the newly added ones:
   ```bash
   ./kk list
   ```

5. Search for specific secrets:
   ```bash
   ./kk search service binance
   ```

6. Retrieve a full secret (requires confirmation):
   ```bash
   ./kk get binance BINANCE_API_KEY
   ```

7. Remove a secret (requires confirmation):
   ```bash
   ./kk remove binance BINANCE_API_KEY
   ```

8. Verify the secret was removed:
   ```bash
   ./kk search service binance
   ```