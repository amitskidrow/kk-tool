import argparse
import sys

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="kk",
        description="Keyring CLI fixed to namespace 'ss' and environment 'dev' for automation-friendly usage.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Secrets live in your system keyring (Secret Service). kk lists masked entries and manages them;\n"
            "automations should fetch values directly via python-keyring. Use the service/username labels shown by kk list.\n"
            "You do not pass namespace/env to keyring.\n\n"
            "DO:\n"
            "- Use keyring.get_password(<service>, <username>) to retrieve secrets.\n"
            "- Keep secrets in-memory only; redact or mask in logs.\n"
            "DON'T:\n"
            "- Scrape kk output or print plaintext secrets.\n\n"
            "Install/run tips:\n"
            "- uv (ephemeral): uv run --with keyring --with secretstorage python -c \"import keyring; print(keyring.get_password('nats','NATS_URL'))\"\n"
            "- pip: pip install keyring secretstorage\n\n"
            "Python example (python-keyring):\n"
            "  import keyring\n"
            "  nats_url = keyring.get_password('nats', 'NATS_URL')\n"
            "  redis_url = keyring.get_password('redis', 'REDIS_URL')\n"
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
