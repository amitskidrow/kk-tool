from ..config import load_config
from ..masking import mask_secret
from ..storage import open_store, list_items


def register(subparsers):
    p = subparsers.add_parser("search", help="Search items in namespace (masked)")
    p.add_argument("query")
    p.set_defaults(func=run)


def run(args):
    cfg = load_config()
    print(f"[{cfg.context_header}]")
    store = open_store(cfg.namespace, cfg.store_mode)
    rows = list_items(store, contains=args.query, env=cfg.default_env)
    print(f"{'Name':<40} {'Secret (masked)'}")
    print("-" * 80)
    for r in rows:
        name = r["name"]
        masked = mask_secret(r["secret"], cfg.mask_visible_ratio)
        print(f"{name:<40} {masked}")
