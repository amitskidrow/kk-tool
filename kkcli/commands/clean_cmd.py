import sys

from ..context import get_context
from ..storage import delete, list_items


def register(subparsers):
    p = subparsers.add_parser(
        "clean",
        help="Delete items in namespace 'ss' (env 'dev'; requires confirmation).",
    )
    p.add_argument("confirm", nargs="?", help="Type 'yes' to confirm destructive delete.")
    p.add_argument("--dry-run", action="store_true", help="Show what would be deleted without removing secrets.")
    p.set_defaults(func=run)


def run(args):
    ctx = get_context()
    cfg = ctx.config
    print(f"[{cfg.context_header}]")
    store = ctx.store
    rows = list_items(store, env=None)
    if args.dry_run:
        print("Dry run — the following items would be deleted:")
        for r in rows:
            print(f" - {r.name}")
        print(f"Total candidates: {len(rows)}")
        return
    if args.confirm != "yes":
        print("This will permanently delete all secrets in namespace 'ss' (env 'dev').")
        print("To proceed run: kk clean yes")
        sys.exit(1)
    count = 0
    for r in rows:
        name = r.name
        try:
            if "/" in name:
                svc, usr = name.split("/", 1)
            else:
                svc = r.attrs.get("service", "")
                usr = r.attrs.get("username", "")
            if svc and usr:
                if delete(store, svc, usr):
                    count += 1
        except Exception:
            continue
    print(f"Deleted {count} item(s) from namespace '{cfg.namespace}'.")
