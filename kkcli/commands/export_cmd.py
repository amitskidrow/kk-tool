import json

from ..config import load_config
from ..storage import export_items, open_store


def register(subparsers):
    p = subparsers.add_parser(
        "export",
        help="Export namespace 'ss' items (env 'dev').",
    )
    p.add_argument("--format", dest="fmt", choices=["json", "env"], default="json")
    p.set_defaults(func=run)


def run(args):
    cfg = load_config()
    header = f"[{cfg.context_header}]"
    store = open_store(cfg.namespace, cfg.store_mode)
    data = export_items(store, fmt=args.fmt, env=None)
    if args.fmt == "json":
        items = json.loads(data) if data else []
        payload = {
            "context": {
                "namespace": cfg.namespace,
                "env": cfg.default_env,
                "store_mode": cfg.store_mode,
            },
            "items": items,
        }
        print(json.dumps(payload))
    else:
        print(header)
        print(data)
