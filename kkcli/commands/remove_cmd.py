import sys

from ..context import get_context
from ..naming import parse_name
from ..output import result_payload
from ..storage import delete, has_item


def register(subparsers):
    p = subparsers.add_parser(
        "remove",
        help="Remove a secret from namespace 'ss' (env 'dev').",
    )
    p.add_argument("name", help="service/username")
    p.add_argument("--no-confirm", action="store_true", help="Skip interactive confirmation.")
    p.add_argument("--dry-run", action="store_true", help="Show whether the secret exists without deleting.")
    p.add_argument("--json", action="store_true", help="Return machine-readable output.")
    p.set_defaults(func=run)


def run(args):
    ctx = get_context()
    cfg = ctx.config
    header = f"[{cfg.context_header}]"
    if not args.json:
        print(header)
    svc, usr = parse_name(args.name)
    store = ctx.store
    exists = has_item(store, svc, usr)
    if args.dry_run:
        if args.json:
            print(
                result_payload(
                    cfg,
                    {
                        "status": "dry-run",
                        "name": f"{svc}/{usr}",
                        "exists": exists,
                    },
                )
            )
        else:
            msg = "exists" if exists else "does not exist"
            print(f"DRY RUN: secret {svc}/{usr} {msg}.")
        return
    if not exists:
        message = "Not found"
        if args.json:
            print(
                result_payload(
                    cfg,
                    {
                        "status": "error",
                        "error": message,
                        "name": f"{svc}/{usr}",
                    },
                )
            )
        else:
            print(message, file=sys.stderr)
        sys.exit(1)
    if not args.no_confirm:
        ans = input(f"Remove secret '{svc}/{usr}'? Type 'yes' to confirm: ")
        if ans.strip() != "yes":
            print("Operation cancelled.")
            return
    delete(store, svc, usr)
    if args.json:
        print(
            result_payload(
                cfg,
                {"status": "ok", "name": f"{svc}/{usr}"},
            )
        )
    else:
        print("Secret removed.")
