from argparse import ArgumentParser
from ..config import load_config
from ..masking import mask_secret
from ..storage import open_store, list_items


def register(subparsers):
    p = subparsers.add_parser("list", help="List namespace items (masked)")
    p.add_argument("--contains", dest="contains", default=None)
    p.add_argument("--env", dest="env", default=None, help="Filter by env (overrides config)")
    p.add_argument("--all-envs", action="store_true", help="Do not filter by env")
    p.set_defaults(func=run)


def run(args):
    cfg = load_config()
    print(f"[{cfg.context_header}]")
    store = open_store(cfg.namespace, cfg.store_mode)
    env_filter = None if args.all_envs else (args.env or cfg.default_env)
    rows = list_items(store, contains=args.contains, env=env_filter)
    print(f"{'Name':<40} {'Secret (masked)'}")
    print("-" * 80)
    for r in rows:
        name = r["name"]
        masked = mask_secret(r["secret"], cfg.mask_visible_ratio)
        print(f"{name:<40} {masked}")
