from pathlib import Path
from ..config import load_config
from ..envparse import parse_env_file, extract_service_name
from ..storage import open_store, put


def register(subparsers):
    p = subparsers.add_parser("ingest", help="Ingest .env files into the namespace store")
    p.add_argument("directory", nargs="?", default=".")
    p.add_argument("--env", dest="env", default=None)
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=run)


def run(args):
    cfg = load_config()
    print(f"[{cfg.context_header}]")
    base = Path(args.directory)
    if not base.exists() or not base.is_dir():
        print(f"Error: {args.directory} is not a directory")
        return
    env_files = list({*base.glob("*.env"), *base.glob(".*.env")})
    if not env_files:
        print("No .env files found")
        return
    def derive_env(p: Path) -> str:
        if args.env:
            return args.env
        name = p.parent.name.lower()
        return name if name in {"prod","production","dev","test","staging"} else cfg.default_env

    store = open_store(cfg.namespace, cfg.store_mode)
    print(f"Found {len(env_files)} .env files:")
    for file in sorted(env_files):
        service = extract_service_name(file.name)
        env_tag = derive_env(file)
        secrets = parse_env_file(file)
        if not secrets:
            print(f"- {file.name}: no secrets")
            continue
        print(f"- {file.name}: service='{service}', {len(secrets)} item(s)")
        for key, value in secrets.items():
            label = f"{service}/{key}"
            attrs = {"service": service, "username": key, "env": env_tag, "source": "ingest"}
            if args.dry_run:
                print(f"  DRY: create [{label}] env={env_tag}")
            else:
                try:
                    put(store, service, key, value, attrs)
                    print(f"  OK:  {label}")
                except Exception as e:
                    print(f"  ERR: {label}: {e}")
