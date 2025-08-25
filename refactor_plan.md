Love the direction. Here’s a tight, implementation-ready plan (no code) to make `kk` consistent, fully namespaced, and predictable—so the CLI and the batch ingestor are two faces of the same system.

# 0) The end state we’re aiming for

* A **single mental model**: every secret is uniquely identified by `service/username` and belongs to a **namespace** (default: `ss`).
* **Two-column UX** everywhere: `Name` (= `service/username`) and `Secret (masked)`.
* **One storage contract** shared by both the CLI and the ingestor. If one writes it, the other can read it—because they both use the same storage layer and the same namespace rules.
* **Isolation from system/global app secrets** by default, so `kk list` shows only what `kk` created (in your namespace), not random app keys.

# 1) Ground rules & constraints

* Backend is still GNOME Keyring / Secret Service (via DBus).
* We want zero interference with other apps’ secrets.
* We want idempotent writes (re-running ingest doesn’t create dupes).
* We want portable, grep-able identifiers in terminals and scripts.

# 2) Namespacing strategy (two options—pick default + allow opt-in)

You have two robust ways to isolate `kk` data. We’ll support both, with **attributes-namespace as the default** to avoid user prompts and friction.

**A) Attribute-based namespace (default)**

* Every item carries attributes:
  `kk_ns = <namespace>` (default `ss`)
  `service = <service>`
  `username = <username>`
  Optional: `env = dev|prod|staging`, `kk_v = 1` (schema version)
* All `kk` CRUD/list/search operations **always** filter by `kk_ns=<value>`.
* Pros: No extra keyring password prompts, works inside the default “Login” collection, zero surprises.
* Cons: Items still live in the default collection (but you never touch others because you always filter on `kk_ns`).

**B) Dedicated collection per namespace (advanced / opt-in)**

* Create/target a collection named `kk:<namespace>` (e.g., `kk:ss`).
* All CRUD/list/search operate only on that collection.
* Still include `kk_ns` attribute for belt-and-suspenders and future migrations.
* Pros: Stronger physical separation; GUI tools clearly show a dedicated keyring.
* Cons: First-time creation can trigger a UI prompt to set/unlock that collection.

**Recommendation:** default to **A**, expose a config toggle to switch to **B** later if you want “hard isolation.”

# 3) Canonical data model (single source of truth)

* **Primary key (logical):** `(kk_ns, service, username)`
* **Label (human-readable):** `service/username` (must be deterministic and match the PK)
* **Secret:** the sensitive value (bytes)
* **Attributes:**

  * Required: `kk_ns`, `service`, `username`
  * Optional: `env`, `source=cli|ingest`, `created_at`, `updated_at` (ISO8601 strings), `kk_v=1`
* **Display “Name”:** `service/username` only. Never show `N/A`.

# 4) Unified storage layer (library) that both CLI & ingestor call

Create a tiny internal “storage contract” (a module) that the CLI and the batch ingestor both use. No one talks to libsecret directly except this layer.

**Public functions of the storage layer (no code here, just interface):**

* `open_store(namespace, mode)` → returns a handle (attribute-filter store by default; or collection store if mode=“collection”)
* `put(namespace, service, username, secret, attrs={...})`

  * Performs an idempotent upsert: search by `(kk_ns, service, username)`, replace the secret, update label to `service/username`.
* `get(namespace, service, username)` → secret
* `delete(namespace, service, username)` → remove item if exists
* `list(namespace, filters)` → iterable of `{name, masked_secret, attrs}`

  * Always filtered by `kk_ns`
  * Order: `service` then `username` (case-insensitive)
* `search(namespace, query)` → like `list` but fuzzy match over `service`, `username`, `label`, `env`

**Why this matters:** both the CLI and the ingestion script become **thin**; they share masking, listing, sorting, and namespace filtering logic—eliminating mismatch.

# 5) CLI and ingestor UX (unified surface)

Rather than two disjoint tools, expose a single CLI with subcommands so behavior stays identical. (You can keep a thin wrapper “ingestor.py” that just calls `kk ingest` for batch flows if you like—but both routes hit the same storage layer.)

**Global flags (apply to all subcommands):**

* `--ns <namespace>` (default: `ss`)
* `--store-mode <attribute|collection>` (default: `attribute`)
* Config file at `~/.config/kk/config.toml` can set defaults (`namespace`, `store_mode`, default `env`, masking policy), overridden by flags.
* Environment variables override config as well (e.g., `KK_NAMESPACE`, `KK_STORE_MODE`).

**Subcommands:**

* `kk list [--env prod|dev|...] [--contains <text>]`
  Only shows items for the namespace. Two columns: `Name`, `Secret (masked)`.
* `kk get <service/username>`
  Confirms before printing full secret to stdout.
* `kk set <service/username> [--value <...>]`
  Interactive prompt if `--value` omitted. Idempotent upsert.
* `kk remove <service/username>`
  Confirmation prompt, then delete.
* `kk search <text>`
  Namespace-filtered fuzzy search; displays in two columns.
* `kk ingest <dir> [--env prod|dev|...] [--dry-run]`
  Batch load `.env` files:

  * `service` = filename stem (`.binance.env` → `binance`)
  * `username` = key (e.g., `BINANCE_SECRET_KEY`)
  * `label` = `service/username`
  * `env` = from flag or derived from directory name (`dev`, `prod`, etc.)
  * Upsert via the same `put(...)`
* `kk export [--format env|json] [--env ...]`
  Exports only namespace items (useful for backups or CI).
* `kk migrate [--from-mode attribute|collection] [--to-mode attribute|collection] [--from-ns ...] [--to-ns ...]`
  Moves items between modes/namespaces safely using the same contract.
* `kk doctor`
  Diagnoses DBus/keyring availability and shows which store you’re pointing at.

# 6) Masking & reveal policy (consistent everywhere)

* Mask rule: show \~30–40% of the prefix, minimum 3 chars visible, always mask at least 1 char. This is safer and consistent across list/search.
* Full reveals only on explicit user confirmation (typed “yes”) or via a `--no-confirm` flag for non-interactive use.
* Never log full secrets; logs reference the `Name` only.

# 7) Consistency and idempotency guarantees

* Every write path (CLI `set`, `ingest`) calls the same `put(...)` which:

  * Finds any existing item by `(kk_ns, service, username)` and replaces it.
  * Enforces the label to equal `service/username`.
  * Updates `updated_at`.
* Every read path uses the same `list/search/get` which:

  * Always scopes to `kk_ns`.
  * Sorts the same way.
  * Applies the same masking logic.

# 8) Isolation from global creds (how we ensure it)

* **Default behavior:** `kk` never calls “list all items.” It **only** calls `search_items` (or equivalent) with the `kk_ns=<namespace>` filter. That alone prevents pulling in Firefox/JetBrains/etc secrets.
* Optional “hard isolation”: point the store to the `kk:<namespace>` collection (if you enable collection mode). You still add the attribute filter as defense-in-depth.

# 9) Config & discoverability

* Defaults live in `~/.config/kk/config.toml`:

  * `namespace = "ss"`
  * `store_mode = "attribute"` (or `"collection"`)
  * `default_env = "dev"`
  * `mask_visible_ratio = 0.35`
* All commands print the effective store context in a header (e.g., `ns=ss, mode=attribute, env=dev`) so it’s obvious what you’re touching.

# 10) Migration plan for your current state

1. Pick your default: start with **attribute mode** (`kk_ns=ss`) to avoid prompts.
2. Run `kk ingest credentials/ --env dev` (dry run first, then real). This re-writes your `.env` items with the namespace and consistent labels.
3. Verify `kk list` only shows namespace items. Your old “global” items remain untouched; you won’t see them because the list is filtered.
4. (Optional) If you want stronger isolation later, run `kk migrate --to-mode collection` to move everything into a new collection `kk:ss`.

# 11) Edge cases & guardrails

* **DBus/headless sessions:** show a helpful error if `org.freedesktop.secrets` isn’t available; suggest starting a keyring daemon or running within a desktop session. For CI, consider a fallback ephemeral in-memory backend (opt-in only).
* **Special chars in `service/username`:** allow alphanumerics, `_`, `-`, `.`, `:`; normalize whitespace to `_`; reject ambiguous names early with a clear message.
* **Long secrets:** list view truncates visually via masking; storage is unaffected.
* **Concurrency:** upserts are single-item and replace atomically; retries on transient DBus errors.
* **Backups:** `kk export --format json` dumps `(kk_ns, service, username, secret, attrs)` for the namespace only.

# 12) Test checklist (before you wire it up)

* Fresh machine, default config → `kk list` shows nothing (good).
* Ingest `.binance.env` and `.coinbase.env` → `kk list` shows exactly those, two columns.
* `kk get binance/BINANCE_SECRET_KEY` → confirm and reveal the exact value.
* `kk search binance` → filters to only binance entries.
* `kk set binance/NEW_KEY` → appears in `kk list`; re-setting updates without dupes.
* Create a random app secret externally → `kk list` still does not show it.
* Switch to collection mode → list shows the same items after migration.

---

