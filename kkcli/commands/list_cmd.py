import json

from ..config import load_config
from ..masking import mask_secret
from ..storage import open_store, list_items


def register(subparsers):
    p = subparsers.add_parser(
        "list",
        help="List secrets in namespace 'ss' (env 'dev'; masked output by default).",
    )
    p.add_argument("--contains", dest="contains", default=None)
    p.add_argument("--json", action="store_true", help="Return machine-readable output.")
    p.set_defaults(func=run)


def run(args):
    cfg = load_config()
    header = f"[{cfg.context_header}]"
    store = open_store(cfg.namespace, cfg.store_mode)
    rows = list_items(store, contains=args.contains, env=None)
    if args.json:
        payload = []
        for r in rows:
            masked = mask_secret(r["secret"], cfg.mask_visible_ratio)
            payload.append(
                {
                    "name": r["name"],
                    "masked_secret": masked,
                    "attrs": r["attrs"],
                }
            )
        print(
            json.dumps(
                {
                    "context": {
                        "namespace": cfg.namespace,
                        "env": cfg.default_env,
                        "store_mode": cfg.store_mode,
                    },
                    "items": payload,
                }
            )
        )
        return
    print(header)
    print(f"{'Name':<40} {'Secret (masked)'}")
    print("-" * 80)
    for r in rows:
        name = r["name"]
        masked = mask_secret(r["secret"], cfg.mask_visible_ratio)
        print(f"{name:<40} {masked}")
