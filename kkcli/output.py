import json
from typing import Iterable, Optional

from .config import Config
from .storage import SecretRow


def context_payload(cfg: Config) -> dict:
    return {
        "namespace": cfg.namespace,
        "env": cfg.default_env,
        "store_mode": cfg.store_mode,
    }


def result_payload(cfg: Config, result: dict) -> str:
    return json.dumps({"context": context_payload(cfg), "result": result})


def masked_items_payload(
    cfg: Config,
    rows: Iterable[SecretRow],
    *,
    query: Optional[str] = None,
) -> str:
    items = []
    for idx, row in enumerate(rows, start=1):
        items.append({
            "index": idx,
            "name": row.name,
            "masked_secret": row.masked_secret(cfg.mask_visible_ratio),
            "attrs": row.attrs,
        })
    payload = {"context": context_payload(cfg), "items": items}
    if query is not None:
        payload["query"] = query
    return json.dumps(payload)


def print_masked_table(cfg: Config, rows: Iterable[SecretRow]) -> None:
    print(f"{'Name':<40} {'Secret (masked)'}")
    print("-" * 80)
    for row in rows:
        print(f"{row.name:<40} {row.masked_secret(cfg.mask_visible_ratio)}")
