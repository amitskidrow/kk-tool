import getpass
import json

from ..config import load_config
from ..naming import parse_name
from ..storage import has_item, open_store, put


def register(subparsers):
    p = subparsers.add_parser(
        "set",
        help="Set or update a secret in namespace 'ss' (env 'dev').",
    )
    p.add_argument("name", help="service/username")
    p.add_argument("--value", dest="value", default=None)
    p.add_argument("--dry-run", action="store_true", help="Show intended action without storing secret.")
    p.add_argument("--json", action="store_true", help="Return machine-readable output.")
    p.set_defaults(func=run)


def run(args):
    cfg = load_config()
    header = f"[{cfg.context_header}]"
    if not args.json:
        print(header)
    svc, usr = parse_name(args.name)
    val = args.value
    if val is None and not args.dry_run:
        val = getpass.getpass("Enter secret: ")
    store = open_store(cfg.namespace, cfg.store_mode)
    existed = has_item(store, svc, usr)
    action = "update" if existed else "create"
    if args.dry_run:
        if args.json:
            print(
                json.dumps(
                    {
                        "context": {
                            "namespace": cfg.namespace,
                            "env": cfg.default_env,
                            "store_mode": cfg.store_mode,
                        },
                        "result": {
                            "status": "dry-run",
                            "action": action,
                            "name": f"{svc}/{usr}",
                        },
                    }
                )
            )
        else:
            message = f"DRY RUN: would {action} secret {svc}/{usr} in namespace '{cfg.namespace}'."
            print(message)
        return
    if val is None:
        raise RuntimeError("Secret value is required when not running in dry-run mode.")
    extra = {"source": "cli", "env": cfg.default_env}
    put(store, svc, usr, val, extra)
    if args.json:
        print(
            json.dumps(
                {
                    "context": {
                        "namespace": cfg.namespace,
                        "env": cfg.default_env,
                        "store_mode": cfg.store_mode,
                    },
                    "result": {
                        "status": "ok",
                        "action": action,
                        "name": f"{svc}/{usr}",
                    },
                }
            )
        )
    else:
        print(f"OK: {svc}/{usr} ({action})")
