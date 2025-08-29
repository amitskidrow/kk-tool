# Repository Guidelines

This repository provides `kk`, a namespace‑aware CLI for GNOME Keyring (Secret Service). Use this guide to contribute safely and consistently.

## Project Structure & Module Organization
- `kkcli/`: Python package with core modules.
  - `__main__.py` (CLI entry), `config.py`, `storage.py`, helpers, and `commands/` (`list`, `search`, `get`, `set`, `remove`, `ingest`, `export`, `migrate`, `doctor`, `clean`).
- `kk`: local runner script (`python` shim).
- `pyproject.toml`: packaging and script entry (`kk`).
- `README.md`, `TESTING.md`: usage and manual test notes.
- `deploy.sh`, `install.sh`: release/install helpers.
- Example inputs: dot‑env files like `.binance.env`, sample creds under `CREDENTIALS/`.

## Build, Test, and Development Commands
- Install (editable): `pip install -e .` or via pipx: `pipx install --force git+https://github.com/amitskidrow/kk-tool@main`.
- Run locally: `./kk --help` or `python -m kkcli list`.
- Smoke check: `kk --version && kk doctor`.
- Deploy helper: `./deploy.sh` (commits, pushes, installs, smoke tests).

## Coding Style & Naming Conventions
- Python ≥3.9, PEP 8, 4‑space indent, type hints where practical; prefer `dataclass` for simple configs (see `config.py`).
- Modules: lowercase; functions/vars: `snake_case`; CLI subcommands: files named `<name>_cmd.py` exposing `register(subparsers)` and `run(args)`.
- Key naming: item label `<service>/<username>`; attributes include `kk_ns`, `service`, `username`, optional `env`, `source`.
- Do not print full secrets except in `get`; use `mask_secret` for listings.

## Testing Guidelines
- No formal test suite yet. Use `TESTING.md` steps to validate core flows (`list`, `ingest --dry-run`, `get`, `remove`).
- If adding tests, prefer `pytest`; place under `tests/` as `test_<module>.py`. Mock Secret Service or gate with markers; never require real secrets in CI.

## Commit & Pull Request Guidelines
- Commits: imperative present (“Add ingest dry‑run summary”), focused, small; include rationale when changing storage semantics or attributes.
- PRs include: description, linked issues, commands to reproduce, sample CLI output (redacted), and notes on env/config (`KK_NAMESPACE`, `KK_STORE_MODE`, `KK_DEFAULT_ENV`).

## Security & Configuration Tips
- Never commit real secrets. Use `.example.env` or `.test.env`. Prefer `ingest --dry-run` first.
- Configure via `~/.config/kk/config.toml` or env vars (`KK_NAMESPACE`, `KK_STORE_MODE`, `KK_DEFAULT_ENV`, `KK_MASK_VISIBLE_RATIO`).
- Be mindful of headless/CI: `kk doctor` helps diagnose Secret Service availability.

