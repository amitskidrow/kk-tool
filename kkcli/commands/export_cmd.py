from ..config import load_config
from ..storage import open_store, export_items


def register(subparsers):
    p = subparsers.add_parser("export", help="Export namespace items")
    p.add_argument("--format", dest="fmt", choices=["json", "env"], default="json")
    p.add_argument("--env", dest="env", default=None)
    p.set_defaults(func=run)


def run(args):
    cfg = load_config()
    store = open_store(cfg.namespace, cfg.store_mode)
    print(export_items(store, fmt=args.fmt, env=args.env))

