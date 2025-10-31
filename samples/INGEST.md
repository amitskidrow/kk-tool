# Sample credentials for local testing

This directory contains sample `.env` files you can ingest with `kk ingest`.

> **Note:** These are **example** values only. They are not real credentials.

## Files

- `.anthropic.env`
- `.nats.env`
- `.redis.env`

## Ingest steps

```bash
./kk ingest samples/ --dry-run
./kk ingest samples/
./kk list
./kk code 1
./kk code nats/NATS_URL --quiet
./kk code 1,3 --json
```
