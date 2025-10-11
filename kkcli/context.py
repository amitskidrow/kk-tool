from dataclasses import dataclass
from functools import lru_cache

from .config import Config, load_config
from .storage import Store, open_store


@dataclass(frozen=True)
class AppContext:
    config: Config
    store: Store


@lru_cache(maxsize=1)
def get_context() -> AppContext:
    cfg = load_config()
    store = open_store(cfg.namespace, cfg.store_mode)
    return AppContext(config=cfg, store=store)
