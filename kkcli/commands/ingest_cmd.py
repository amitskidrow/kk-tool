from pathlib import Path

from ..context import get_context
from ..envparse import parse_env_file, extract_service_name
from ..storage import has_item, put


def register(subparsers):
    p = subparsers.add_parser(
        "ingest",
        help="Ingest dot-env files into namespace 'ss' (env 'dev').",
    )
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=run)


def run(args):
    ctx = get_context()
    cfg = ctx.config
    print(f"[{cfg.context_header}]")
    base = Path(args.path)
    if not base.exists():
        print(f"Error: {args.path} does not exist")
        return
    # Support single .env file path or recursive directory scan
    env_files = []
    if base.is_file():
        if base.name.endswith(".env"):
            env_files = [base]
        else:
            print(f"Error: {args.path} is not a .env file")
            return
    elif base.is_dir():
        # Recursive scan; only consider dot-notation .env files: .<name>.env
        env_files = [p for p in base.rglob("*.env") if p.name.startswith(".")]
    else:
        print(f"Error: {args.path} is not a file or directory")
        return
    if not env_files:
        print("No .env files found")
        return
    store = ctx.store
    print(f"Found {len(env_files)} dot-env file(s):")

    rows = []  # Collect summary rows
    for file in sorted(env_files):
        service = extract_service_name(file.name)
        env_tag = cfg.default_env
        secrets = parse_env_file(file)
        if not secrets:
            rows.append({"name": str(file), "action": "skip", "env": env_tag, "msg": "no secrets"})
            continue
        for key, value in secrets.items():
            label = f"{service}/{key}"
            attrs = {"env": env_tag, "source": "ingest"}
            if args.dry_run:
                action = "create" if not has_item(store, service, key) else "update"
                rows.append({"name": label, "action": f"DRY-{action}", "env": env_tag, "msg": ""})
                continue
            try:
                result = put(store, service, key, value, attrs)
                rows.append({"name": label, "action": result, "env": env_tag, "msg": ""})
            except Exception as e:
                rows.append({"name": label, "action": "error", "env": env_tag, "msg": str(e)})

    # Print summary table
    if not rows:
        print("Nothing to ingest")
        return
    name_w = max(4, max(len(r["name"]) for r in rows))
    act_w = max(6, max(len(r["action"]) for r in rows))
    env_w = max(3, max(len(r["env"]) for r in rows))
    print(f"{'Name':<{name_w}}  {'Action':<{act_w}}  {'Env':<{env_w}}  Message")
    print("-" * (name_w + act_w + env_w + 4 + 8))
    totals = {"created": 0, "updated": 0, "skip": 0, "error": 0}
    for r in rows:
        print(f"{r['name']:<{name_w}}  {r['action']:<{act_w}}  {r['env']:<{env_w}}  {r['msg']}")
        if r["action"].startswith("DRY-"):
            continue
        if r["action"] in totals:
            totals[r["action"]] += 1
    print("-")
    print(
        f"Totals: created={totals['created']}, updated={totals['updated']}, skipped={totals['skip']}, errors={totals['error']}"
    )
