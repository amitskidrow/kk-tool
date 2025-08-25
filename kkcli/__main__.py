import argparse
import sys

from .config import load_config
from . import __version__


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="kk", description="Namespace-aware keyring CLI")
    sp = p.add_subparsers(dest="cmd")

    # Register subcommands
    from .commands import list_cmd, search_cmd, get_cmd, set_cmd, remove_cmd, ingest_cmd, export_cmd, migrate_cmd, doctor_cmd
    list_cmd.register(sp)
    search_cmd.register(sp)
    get_cmd.register(sp)
    set_cmd.register(sp)
    remove_cmd.register(sp)
    ingest_cmd.register(sp)
    export_cmd.register(sp)
    migrate_cmd.register(sp)
    doctor_cmd.register(sp)

    # Global options via env/config; kept minimal in CLI
    p.add_argument("--ns", dest="namespace", default=None, help="Override namespace")
    p.add_argument("--store-mode", dest="store_mode", choices=["attribute", "collection"], default=None, help="Override store mode")
    p.add_argument(
        "--version",
        action="version",
        version=f"kk {__version__}",
        help="Show version and exit",
    )
    return p


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    # --version is handled by argparse action
    # Allow overrides of config via flags
    if args.namespace:
        import os
        os.environ["KK_NAMESPACE"] = args.namespace
    if args.store_mode:
        import os
        os.environ["KK_STORE_MODE"] = args.store_mode
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args) or 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
