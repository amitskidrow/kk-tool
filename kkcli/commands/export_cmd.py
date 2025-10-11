import json

from ..context import get_context
from ..output import context_payload
from ..storage import export_items


def register(subparsers):
    p = subparsers.add_parser(
        "export",
        help="Export namespace 'ss' items (env 'dev').",
    )
    p.add_argument("--format", dest="fmt", choices=["json", "env"], default="json")
    p.set_defaults(func=run)


def run(args):
    ctx = get_context()
    cfg = ctx.config
    header = f"[{cfg.context_header}]"
    store = ctx.store
    data = export_items(store, fmt=args.fmt, env=None)
    if args.fmt == "json":
        items = json.loads(data) if data else []
        payload = {
            "context": context_payload(cfg),
            "items": items,
        }
        print(json.dumps(payload))
    else:
        print(header)
        print(data)
