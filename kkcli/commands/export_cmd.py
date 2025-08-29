from ..config import load_config
from ..storage import open_store, export_items


def register(subparsers):
    p = subparsers.add_parser("export", help="Export namespace items")
    p.add_argument("--format", dest="fmt", choices=["json", "env"], default="json")
    p.add_argument("--env", dest="env", default=None, help="Filter by env (overrides config)")
    p.add_argument("--all-envs", action="store_true", help="Do not filter by env")
    p.set_defaults(func=run)


def run(args):
    cfg = load_config()
    store = open_store(cfg.namespace, cfg.store_mode)
    env_filter = None if args.all_envs else (args.env or cfg.default_env)
    print(export_items(store, fmt=args.fmt, env=env_filter))
