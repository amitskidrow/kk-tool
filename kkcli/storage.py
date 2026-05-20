# kkcli/storage.py
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple, Union

from .logger import get_logger

logger = get_logger()

# Try to import secretstorage; optional for headless fallback
try:
    import secretstorage  # type: ignore
except Exception as e:  # pragma: no cover
    logger.debug(f"Failed to import secretstorage: {e}")
    secretstorage = None  # noqa: N816


class BaseStore(ABC):
    """Abstract Base Class for storage backends."""
    
    @abstractmethod
    def list(self, *, contains: Optional[str] = None, env: Optional[str] = None) -> List['SecretRow']:
        pass

    @abstractmethod
    def get(self, service: str, username: str) -> Optional[str]:
        pass

    @abstractmethod
    def put(self, service: str, username: str, secret: str, extra: Optional[Dict[str, str]] = None) -> str:
        pass

    @abstractmethod
    def delete(self, service: str, username: str) -> bool:
        pass



@dataclass
class SecretRow:
    name: str
    secret: Optional[Union[str, bytes]]
    attrs: Dict[str, str]

    def secret_text(self) -> str:
        s = self.secret
        if s is None:
            return ""
        if isinstance(s, (bytes, bytearray)):
            try:
                return s.decode()
            except Exception:
                return s.decode(errors="ignore")
        return str(s)

    def masked_secret(self, visible_ratio: float = 0.35, min_visible: int = 3) -> str:
        from .masking import mask_secret
        return mask_secret(self.secret_text(), visible_ratio, min_visible)


# ------------------------- FileStore (headless/CI) -------------------------

class FileStore(BaseStore):
    """Simple JSON file store, opt-in via KK_FAKE_STORE=1 or KK_STORE=fake."""
    def __init__(self, path: Optional[str] = None, namespace: str = "ss") -> None:
        self.ns = namespace
        if path is None:
            data_home = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
            path = os.path.join(data_home, "kk-tool", "fake_store.json")
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._data: Dict[str, Dict[str, str]] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load FileStore from {self.path}: {e}")
                self._data = {}

    def _save(self) -> None:
        tmp = self.path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, sort_keys=True)
            os.replace(tmp, self.path)
        except Exception as e:
            logger.error(f"Failed to save FileStore to {self.path}: {e}")

    @staticmethod
    def _key(ns: str, service: str, username: str) -> str:
        return f"{ns}:{service}/{username}"

    def list(self, *, contains: Optional[str] = None, env: Optional[str] = None) -> List[SecretRow]:
        rows: List[SecretRow] = []
        needle = (contains or "").lower()
        for k, rec in self._data.items():
            if not k.startswith(f"{self.ns}:"):
                continue
            name = k.split(":", 1)[1]
            svc = rec.get("service", "")
            usr = rec.get("username", "")
            aenv = rec.get("env", "")
            if env and aenv != env:
                continue
            hay = " ".join([svc, usr, name, aenv]).lower()
            if needle and needle not in hay:
                continue
            rows.append(SecretRow(name=name, secret=rec.get("secret", ""), attrs=rec))
        rows.sort(key=lambda r: (r.attrs.get("service", "").lower(), r.attrs.get("username", "").lower()))
        return rows

    def get(self, service: str, username: str) -> Optional[str]:
        rec = self._data.get(self._key(self.ns, service, username))
        return rec.get("secret") if rec else None

    def put(self, service: str, username: str, secret: str, extra: Optional[Dict[str, str]] = None) -> str:
        key = self._key(self.ns, service, username)
        existed = key in self._data
        now = datetime.now(timezone.utc).isoformat()
        base = {"kk_ns": self.ns, "service": service, "username": username, "secret": secret}
        if extra:
            base.update({k: str(v) for k, v in extra.items()})
        base.setdefault("created_at", now)
        base["updated_at"] = now
        self._data[key] = base
        self._save()
        return "updated" if existed else "created"

    def delete(self, service: str, username: str) -> bool:
        existed = self._data.pop(self._key(self.ns, service, username), None) is not None
        if existed:
            self._save()
        return existed



# ----------------------- Secret Service store (default) -----------------------

class SecretServiceStore(BaseStore):
    def __init__(self, namespace: str, mode: str = "attribute") -> None:
        if secretstorage is None:
            raise RuntimeError("python-secretstorage not installed. Install it or set KK_FAKE_STORE=1.")
        bus = secretstorage.dbus_init()
        if mode == "collection":
            label = f"kk:{namespace}"
            coll = None
            for c in secretstorage.get_all_collections(bus):
                try:
                    if c.get_label() == label:
                        coll = c
                        break
                except Exception as e:
                    logger.debug(f"Error checking collection label: {e}")
                    continue
            if coll is None:
                coll = secretstorage.create_collection(bus, label, "")
            if coll.is_locked():
                coll.unlock()
            self.collection = coll
        else:
            coll = secretstorage.get_default_collection(bus)
            if coll.is_locked():
                coll.unlock()
            self.collection = coll
        self.ns = namespace
        self.mode = mode

    def _search(self, attrs: Dict[str, str]):
        return self.collection.search_items(attrs)

    def _find(self, service: str, username: str):
        target = {"kk_ns": self.ns, "service": service, "username": username}
        for it in self._search(target):
            return it
        return None

    def list(self, *, contains: Optional[str] = None, env: Optional[str] = None) -> List[SecretRow]:
        items = self._search({"kk_ns": self.ns})
        rows: List[SecretRow] = []
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
                sec = it.get_secret()
                rows.append(SecretRow(name=label, secret=sec, attrs=attrs))
            except Exception as e:
                logger.debug(f"Failed to process item in list: {e}")
                continue
        rows.sort(key=lambda r: (r.attrs.get("service", "").lower(), r.attrs.get("username", "").lower()))
        return rows

    def get(self, service: str, username: str) -> Optional[str]:
        it = self._find(service, username)
        if not it:
            return None
        try:
            if it.is_locked():
                it.unlock()
            sec = it.get_secret()
            return sec.decode(errors="replace")
        except Exception as e:
            logger.error(f"Failed to get secret for {service}/{username}: {e}")
            return None

    def put(self, service: str, username: str, secret: str, extra: Optional[Dict[str, str]] = None) -> str:
        label = f"{service}/{username}"
        now = datetime.now(timezone.utc).isoformat()
        base = {"kk_ns": self.ns, "service": service, "username": username, "kk_v": "1"}
        if extra:
            base.update({k: str(v) for k, v in extra.items()})
        
        it = self._find(service, username)
        if it:
            try:
                if it.is_locked():
                    it.unlock()
                old = it.get_attributes() or {}
                # Preserve existing attributes not managed by us
                merged = {k: v for k, v in old.items() if k not in {"kk_ns", "service", "username", "kk_v", "updated_at"}}
                merged.update(base)
                if "created_at" in old:
                    merged["created_at"] = old["created_at"]
                else:
                    merged.setdefault("created_at", now)
                merged["updated_at"] = now
                
                it.set_label(label)
                it.set_attributes(merged)
                it.set_secret(secret.encode())
                return "updated"
            except Exception as e:
                logger.warning(f"Failed to update item {label}, will try to recreate: {e}")
                try:
                    it.delete()
                except Exception as de:
                    logger.error(f"Failed to delete old item for {label}: {de}")
                    # Continue to create attempt anyway
        
        base.setdefault("created_at", now)
        base["updated_at"] = now
        self.collection.create_item(label, base, secret.encode(), False)
        return "created"

    def delete(self, service: str, username: str) -> bool:
        it = self._find(service, username)
        if not it:
            return False
        try:
            it.delete()
            return True
        except Exception as e:
            logger.error(f"Failed to delete item {service}/{username}: {e}")
            return False



# ---------------------------- Public helpers ---------------------------------

class Store:
    """Facade that unifies FileStore and SecretServiceStore signatures."""
    def __init__(self, backend, namespace: str):
        self._b = backend
        self.namespace = namespace

    def list(self, **kw) -> List[SecretRow]:
        return self._b.list(**kw)

    def get(self, service: str, username: str) -> Optional[str]:
        return self._b.get(service, username)

    def put(self, service: str, username: str, secret: str, extra: Optional[Dict[str, str]] = None) -> str:
        return self._b.put(service, username, secret, extra)

    def remove(self, service: str, username: str) -> bool:
        return self._b.delete(service, username)


def open_store(namespace: str, mode: str = "attribute") -> Store:
    use_fake = os.environ.get("KK_FAKE_STORE") == "1" or os.environ.get("KK_STORE") == "fake"
    if use_fake:
        return Store(FileStore(namespace=namespace), namespace)
    if secretstorage is None:
        raise RuntimeError("python-secretstorage not installed. Set KK_FAKE_STORE=1 for headless fallback.")
    try:
        return Store(SecretServiceStore(namespace, mode=mode), namespace)
    except Exception as e:
        # Hint to switch if desired
        raise RuntimeError(
            "Secret Service unavailable. Start a session keyring or set KK_FAKE_STORE=1 for headless operation."
        ) from e


def list_items(store: Store, contains: Optional[str] = None, env: Optional[str] = None) -> List[SecretRow]:
    return store.list(contains=contains, env=env)


def get(store: Store, service: str, username: str) -> Optional[str]:
    return store.get(service, username)


def has_item(store: Store, service: str, username: str) -> bool:
    return get(store, service, username) is not None


def put(store: Store, service: str, username: str, secret: str, attrs: Optional[Dict[str, str]] = None) -> str:
    return store.put(service, username, secret, attrs)


def delete(store: Store, service: str, username: str) -> bool:
    return store.remove(service, username)


def export_items(store: Store, fmt: str = "json", env: Optional[str] = None) -> str:
    import json
    rows = list_items(store, env=env)
    if fmt == "env":
        # Dump as .env-style with names as comments and username=value under service groups
        out_lines: List[str] = []
        current_service = None
        for r in rows:
            svc = r.attrs.get("service", "")
            usr = r.attrs.get("username", "")
            if svc != current_service:
                out_lines.append("")
                out_lines.append(f"## service: {svc}")
                current_service = svc
            val = r.secret_text()
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
                "service": r.attrs.get("service"),
                "username": r.attrs.get("username"),
                "secret": r.secret_text(),
                "attrs": r.attrs,
            }
            for r in rows
        ]
        return json.dumps(payload, indent=2)


def migrate(from_store: Store, to_store: Store) -> int:
    count = 0
    for r in list_items(from_store):
        svc = r.attrs.get("service", "")
        usr = r.attrs.get("username", "")
        val = r.secret_text()
        extra = {k: v for k, v in r.attrs.items() if k not in {"kk_ns", "service", "username"}}
        put(to_store, svc, usr, val, extra)
        count += 1
    return count
