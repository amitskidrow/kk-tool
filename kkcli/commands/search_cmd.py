from ..context import get_context
from ..output import masked_items_payload, print_masked_table
from ..storage import list_items


def register(subparsers):
    p = subparsers.add_parser(
        "search",
        help="Search secrets in namespace 'ss' (env 'dev'; masked output by default).",
    )
    p.add_argument("query")
    p.add_argument("--json", action="store_true", help="Return machine-readable output.")
    p.set_defaults(func=run)


def run(args):
    ctx = get_context()
    cfg = ctx.config
    header = f"[{cfg.context_header}]"
    store = ctx.store
    rows = list_items(store, contains=args.query, env=None)
    if args.json:
        print(masked_items_payload(cfg, rows, query=args.query))
        return
    print(header)
    print_masked_table(cfg, rows)
