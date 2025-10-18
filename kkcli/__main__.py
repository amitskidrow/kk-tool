import argparse
import sys

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="kk",
        description="Keyring CLI fixed to namespace 'ss' and environment 'dev' for automation-friendly usage.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Automation guidance:\n"
            "- Call the Secret Service API with a keyring client (e.g. python-keyring) to fetch secrets.\n"
            "- Do not spawn `kk list` (or other kk commands) in a subprocess to scrape masked output.\n"
            "- When you retrieve a secret via the keyring, keep it in-memory and never log or display the plaintext.\n\n"
            "Python example (using kk's storage helpers):\n"
            "  from kkcli.storage import open_store, get\n"
            "  store = open_store('ss', 'attribute')  # namespace='ss', mode='attribute'\n"
            "  nats_url = get(store, 'nats', 'NATS_URL')\n"
            "  redis_url = get(store, 'redis', 'REDIS_URL')\n"
            "  print(nats_url)\n"
            "  print(redis_url)\n"
        ),
    )
    sp = p.add_subparsers(dest="cmd")

    # Register subcommands
    from .commands import list_cmd, search_cmd, get_cmd, set_cmd, remove_cmd, ingest_cmd, export_cmd, migrate_cmd, doctor_cmd, clean_cmd
    list_cmd.register(sp)
    search_cmd.register(sp)
    get_cmd.register(sp)
    set_cmd.register(sp)
    remove_cmd.register(sp)
    ingest_cmd.register(sp)
    export_cmd.register(sp)
    migrate_cmd.register(sp)
    doctor_cmd.register(sp)
    clean_cmd.register(sp)

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
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args) or 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
