from ..config import load_config
from ..storage import open_store, migrate


def register(subparsers):
    p = subparsers.add_parser("migrate", help="Migrate items between modes/namespaces")
    p.add_argument("--from-mode", dest="from_mode", choices=["attribute", "collection"], default=None)
    p.add_argument("--to-mode", dest="to_mode", choices=["attribute", "collection"], default=None)
    p.add_argument("--from-ns", dest="from_ns", default=None)
    p.add_argument("--to-ns", dest="to_ns", default=None)
    p.set_defaults(func=run)


def run(args):
    cfg = load_config()
    from_ns = args.from_ns or cfg.namespace
    to_ns = args.to_ns or cfg.namespace
    from_mode = args.from_mode or cfg.store_mode
    to_mode = args.to_mode or cfg.store_mode
    src = open_store(from_ns, from_mode)
    dst = open_store(to_ns, to_mode)
    moved = migrate(src, dst)
    print(f"Migrated {moved} items from ns={from_ns},mode={from_mode} to ns={to_ns},mode={to_mode}")

