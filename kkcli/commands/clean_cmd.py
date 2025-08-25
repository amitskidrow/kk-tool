import sys
from ..config import load_config
from ..storage import open_store, list_items, delete


def register(subparsers):
    p = subparsers.add_parser("clean", help="Delete all items in current namespace (requires 'yes')")
    p.add_argument("confirm", nargs="?", help="Type 'yes' to confirm")
    p.set_defaults(func=run)


def run(args):
    cfg = load_config()
    print(f"[{cfg.context_header}]")
    if args.confirm != "yes":
        print("This will permanently delete all items in the namespace.")
        print("Type: kk clean yes")
        sys.exit(1)
    store = open_store(cfg.namespace, cfg.store_mode)
    rows = list_items(store, env=cfg.default_env)
    count = 0
    for r in rows:
        name = r.get("name", "")
        try:
            if "/" in name:
                svc, usr = name.split("/", 1)
            else:
                svc = r["attrs"].get("service", "")
                usr = r["attrs"].get("username", "")
            if svc and usr:
                if delete(store, svc, usr):
                    count += 1
        except Exception:
            continue
    print(f"Deleted {count} item(s) from namespace '{cfg.namespace}' and env '{cfg.default_env}'.")

