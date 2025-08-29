import datetime as _dt
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


def _ensure_secretstorage():
    try:
        import secretstorage  # noqa: F401
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "Missing dependency: python-secretstorage. Install via 'pip install secretstorage'"
        ) from e


@dataclass
class Store:
    namespace: str
    mode: str  # "attribute" or "collection"
    bus: object
    collection: object


def open_store(namespace: str, mode: str = "attribute") -> Store:
    _ensure_secretstorage()
    import secretstorage

    bus = secretstorage.dbus_init()
    if mode == "collection":
        label = f"kk:{namespace}"
        # Try to find existing collection by label
        for coll in secretstorage.get_all_collections(bus):
            try:
                if coll.get_label() == label:
                    if coll.is_locked():
                        coll.unlock()
                    return Store(namespace, mode, bus, coll)
            except Exception:
                continue
        # Create if missing
        coll = secretstorage.create_collection(bus, label, '')
        if coll.is_locked():
            coll.unlock()
        return Store(namespace, mode, bus, coll)
    else:
        coll = secretstorage.get_default_collection(bus)
        if coll.is_locked():
            coll.unlock()
        return Store(namespace, "attribute", bus, coll)


def _now_iso() -> str:
    return _dt.datetime.utcnow().replace(tzinfo=_dt.timezone.utc).isoformat()


def _attrs_for(namespace: str, service: str, username: str, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    attrs = {
        "kk_ns": namespace,
        "service": service,
        "username": username,
        "kk_v": "1",
    }
    if extra:
        attrs.update({k: str(v) for k, v in extra.items()})
    return attrs


def _find_item(store: Store, service: str, username: str):
    # Always include namespace filter
    target = {"kk_ns": store.namespace, "service": service, "username": username}
    for it in store.collection.search_items(target):
        return it
    return None


def has_item(store: Store, service: str, username: str) -> bool:
    return _find_item(store, service, username) is not None


def put(store: Store, service: str, username: str, secret: str, attrs: Optional[Dict[str, str]] = None) -> None:
    label = f"{service}/{username}"
    a = _attrs_for(store.namespace, service, username, attrs)
    existing = _find_item(store, service, username)
    if existing:
        try:
            # Replace secret and refresh attributes/label
            if existing.is_locked():
                existing.unlock()
            existing.set_label(label)
            # Preserve created_at if present; always refresh updated_at
            try:
                old_attrs = existing.get_attributes() or {}
            except Exception:
                old_attrs = {}
            if "created_at" in old_attrs:
                a["created_at"] = old_attrs["created_at"]
            a["updated_at"] = _now_iso()
            existing.set_attributes(a)
            existing.set_secret(secret.encode())
            return
        except Exception:
            try:
                existing.delete()
            except Exception:
                pass
    # Create new item
    a.setdefault("created_at", _now_iso())
    a["updated_at"] = _now_iso()
    # secretstorage>=3.3.0 signature: (label, attributes, secret, replace=False, content_type='text/plain')
    store.collection.create_item(label, a, secret.encode(), False)


def get(store: Store, service: str, username: str) -> Optional[str]:
    it = _find_item(store, service, username)
    if not it:
        return None
    if it.is_locked():
        it.unlock()
    sec = it.get_secret()
    try:
        return sec.decode()
    except Exception:
        return sec.decode(errors="ignore")


def delete(store: Store, service: str, username: str) -> bool:
    it = _find_item(store, service, username)
    if not it:
        return False
    it.delete()
    return True


def list_items(store: Store, contains: Optional[str] = None, env: Optional[str] = None) -> List[dict]:
    # Filter by namespace first
    items = store.collection.search_items({"kk_ns": store.namespace})
    rows: List[dict] = []
    needle = (contains or "").lower()
    for it in items:
        try:
            attrs = it.get_attributes() or {}
            if env and attrs.get("env") != env:
                continue
            svc = attrs.get("service", "")
            usr = attrs.get("username", "")
            label = f"{svc}/{usr}" if svc and usr else (it.get_label() or "")
            hay = " ".join([svc, usr, label, attrs.get("env", "")]).lower()
            if needle and needle not in hay:
                continue
            if it.is_locked():
                it.unlock()
            secret = it.get_secret()
            rows.append({"name": label, "secret": secret, "attrs": attrs})
        except Exception:
            continue
    rows.sort(key=lambda r: (r["attrs"].get("service", "").lower(), r["attrs"].get("username", "").lower()))
    return rows


def search(store: Store, query: str) -> List[dict]:
    return list_items(store, contains=query)


def export_items(store: Store, fmt: str = "json", env: Optional[str] = None) -> str:
    import json
    rows = list_items(store, env=env)
    if fmt == "env":
        # Dump as .env-style with names as comments and username=value under service groups
        out_lines: List[str] = []
        current_service = None
        for r in rows:
            svc = r["attrs"].get("service", "")
            usr = r["attrs"].get("username", "")
            if svc != current_service:
                out_lines.append("")
                out_lines.append(f"## service: {svc}")
                current_service = svc
            try:
                val = r["secret"].decode()
            except Exception:
                val = r["secret"].decode(errors="ignore")
            # Quote and escape to be .env-safe
            safe = (
                val.replace("\\", "\\\\")
                   .replace("\n", "\\n")
                   .replace('"', '\\"')
            )
            out_lines.append(f"{usr}=\"{safe}\"")
        return "\n".join(out_lines).lstrip()
    else:
        payload = [
            {
                "kk_ns": store.namespace,
                "service": r["attrs"].get("service"),
                "username": r["attrs"].get("username"),
                "secret": (r["secret"].decode(errors="ignore") if isinstance(r["secret"], (bytes, bytearray)) else str(r["secret"])) ,
                "attrs": r["attrs"],
            }
            for r in rows
        ]
        return json.dumps(payload, indent=2)


def migrate(from_store: Store, to_store: Store) -> int:
    count = 0
    rows = list_items(from_store)
    for r in rows:
        svc = r["attrs"].get("service", "")
        usr = r["attrs"].get("username", "")
        try:
            val = r["secret"].decode()
        except Exception:
            val = r["secret"].decode(errors="ignore")
        extra = {k: v for k, v in r["attrs"].items() if k not in {"kk_ns", "service", "username"}}
        put(to_store, svc, usr, val, extra)
        count += 1
    return count
