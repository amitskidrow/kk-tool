import sys
from ..config import load_config
from ..naming import parse_name
from ..storage import open_store, delete


def register(subparsers):
    p = subparsers.add_parser("remove", help="Remove a secret (confirm)")
    p.add_argument("name", help="service/username")
    p.add_argument("--no-confirm", action="store_true")
    p.set_defaults(func=run)


def run(args):
    cfg = load_config()
    print(f"[{cfg.context_header}]")
    svc, usr = parse_name(args.name)
    if not args.no_confirm:
        ans = input(f"Remove secret '{svc}/{usr}'? Type 'yes' to confirm: ")
        if ans.strip() != "yes":
            print("Operation cancelled.")
            return
    store = open_store(cfg.namespace, cfg.store_mode)
    ok = delete(store, svc, usr)
    if not ok:
        print("Not found", file=sys.stderr)
        sys.exit(1)
    print("Secret removed.")

