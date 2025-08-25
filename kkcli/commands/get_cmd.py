import sys
from ..config import load_config
from ..naming import parse_name
from ..storage import open_store, get as get_item


def register(subparsers):
    p = subparsers.add_parser("get", help="Get full secret")
    p.add_argument("name", help="service/username")
    p.set_defaults(func=run)


def run(args):
    cfg = load_config()
    print(f"[{cfg.context_header}]")
    svc, usr = parse_name(args.name)
    store = open_store(cfg.namespace, cfg.store_mode)
    val = get_item(store, svc, usr)
    if val is None:
        print("Not found", file=sys.stderr)
        sys.exit(1)
    print(val)
