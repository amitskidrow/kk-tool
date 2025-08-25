import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import tomllib  # Python 3.11+
except Exception:  # pragma: no cover
    tomllib = None  # type: ignore


@dataclass
class Config:
    namespace: str = "ss"
    store_mode: str = "attribute"  # or "collection"
    default_env: str = "dev"
    mask_visible_ratio: float = 0.35

    @property
    def context_header(self) -> str:
        return f"ns={self.namespace}, mode={self.store_mode}, env={self.default_env}"


def _from_toml(path: Path) -> dict:
    if not path.exists() or not path.is_file():
        return {}
    if tomllib is None:
        return {}
    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
        return data or {}
    except Exception:
        return {}


def load_config() -> Config:
    # Defaults
    cfg = Config()
    # TOML
    toml_path = Path(os.environ.get("KK_CONFIG", ""))
    if not toml_path:
        toml_path = Path.home() / ".config" / "kk" / "config.toml"
    data = _from_toml(toml_path)
    if isinstance(data, dict):
        kk = data.get("kk") if "kk" in data else data
        if isinstance(kk, dict):
            cfg.namespace = str(kk.get("namespace", cfg.namespace))
            cfg.store_mode = str(kk.get("store_mode", cfg.store_mode))
            cfg.default_env = str(kk.get("default_env", cfg.default_env))
            try:
                cfg.mask_visible_ratio = float(kk.get("mask_visible_ratio", cfg.mask_visible_ratio))
            except Exception:
                pass

    # ENV overrides
    cfg.namespace = os.environ.get("KK_NAMESPACE", cfg.namespace)
    cfg.store_mode = os.environ.get("KK_STORE_MODE", cfg.store_mode)
    cfg.default_env = os.environ.get("KK_DEFAULT_ENV", cfg.default_env)
    try:
        ratio_env = os.environ.get("KK_MASK_VISIBLE_RATIO")
        if ratio_env:
            cfg.mask_visible_ratio = float(ratio_env)
    except Exception:
        pass

    # Normalize store_mode
    if cfg.store_mode not in ("attribute", "collection"):
        cfg.store_mode = "attribute"
    return cfg

