import sys
from ..config import load_config
from ..storage import open_store, list_items, delete


def register(subparsers):
    p = subparsers.add_parser(
        "clean",
        help="Delete items in current namespace and env (requires 'yes')",
    )
    p.add_argument("confirm", nargs="?", help="Type 'yes' to confirm")
    p.add_argument("--env", dest="env", default=None, help="Filter by env (overrides config)")
    p.add_argument("--all-envs", action="store_true", help="Do not filter by env (delete across all envs)")
    p.set_defaults(func=run)


def run(args):
    cfg = load_config()
    print(f"[{cfg.context_header}]")
    if args.confirm != "yes":
        print("This will permanently delete items in the namespace.")
        print("By default only the current env is affected; use --all-envs to delete across all envs.")
        print("Type: kk clean yes")
        sys.exit(1)
    store = open_store(cfg.namespace, cfg.store_mode)
    env_filter = None if args.all_envs else (args.env or cfg.default_env)
    rows = list_items(store, env=env_filter)
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
    env_label = "ALL" if env_filter is None else env_filter
    print(f"Deleted {count} item(s) from namespace '{cfg.namespace}' and env '{env_label}'.")
