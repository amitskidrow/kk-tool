import getpass
from ..config import load_config
from ..naming import parse_name
from ..storage import open_store, put


def register(subparsers):
    p = subparsers.add_parser("set", help="Set or update a secret")
    p.add_argument("name", help="service/username")
    p.add_argument("--value", dest="value", default=None)
    p.add_argument("--env", dest="env", default=None)
    p.set_defaults(func=run)


def run(args):
    cfg = load_config()
    print(f"[{cfg.context_header}]")
    svc, usr = parse_name(args.name)
    val = args.value
    if val is None:
        val = getpass.getpass("Enter secret: ")
    store = open_store(cfg.namespace, cfg.store_mode)
    extra = {"source": "cli"}
    if args.env:
        extra["env"] = args.env
    put(store, svc, usr, val, extra)
    print(f"OK: {svc}/{usr}")

