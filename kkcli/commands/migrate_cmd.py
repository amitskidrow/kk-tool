from ..context import get_context
from ..storage import migrate, open_store


def register(subparsers):
    p = subparsers.add_parser(
        "migrate",
        help="Migrate items between storage modes within namespace 'ss'.",
    )
    p.add_argument("--from-mode", dest="from_mode", choices=["attribute", "collection"], default=None)
    p.add_argument("--to-mode", dest="to_mode", choices=["attribute", "collection"], default=None)
    p.set_defaults(func=run)


def run(args):
    ctx = get_context()
    cfg = ctx.config
    print(f"[{cfg.context_header}]")
    from_mode = args.from_mode or cfg.store_mode
    to_mode = args.to_mode or cfg.store_mode
    src = open_store(cfg.namespace, from_mode)
    dst = open_store(cfg.namespace, to_mode)
    moved = migrate(src, dst)
    print(f"Migrated {moved} item(s) in namespace '{cfg.namespace}' from mode={from_mode} to mode={to_mode}")
