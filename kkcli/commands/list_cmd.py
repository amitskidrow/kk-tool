import argparse
import json

from ..config import load_config
from ..masking import mask_secret
from ..storage import open_store, list_items


def register(subparsers):
    p = subparsers.add_parser(
        "list",
        help="Show masked secrets for manual checks; automations must use keyring APIs instead.",
        description=(
            "Produces a masked table of secrets so humans can confirm what exists.\n"
            "Agentic CLIs should query the Secret Service directly via a keyring client\n"
            "(e.g. python-keyring) rather than scraping this masked output. Never display\n"
            "or log unmasked secrets after fetching them from the keyring."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--contains", dest="contains", default=None)
    p.add_argument("--json", action="store_true", help="Return machine-readable output.")
    p.set_defaults(func=run)


def run(args):
    cfg = load_config()
    header = f"[{cfg.context_header}]"
    store = open_store(cfg.namespace, cfg.store_mode)
    rows = list_items(store, contains=args.contains, env=None)
    if args.json:
        payload = []
        for r in rows:
            masked = mask_secret(r["secret"], cfg.mask_visible_ratio)
            payload.append(
                {
                    "name": r["name"],
                    "masked_secret": masked,
                    "attrs": r["attrs"],
                }
        )
        print(
            json.dumps(
                {
                    "context": {
                        "namespace": cfg.namespace,
                        "env": cfg.default_env,
                        "store_mode": cfg.store_mode,
                    },
                    "items": payload,
                }
            )
        )
        return
    note_lines = [
        "NOTE: Masked output is provided for manual inspection only.",
        "Agents must call the Secret Service/keyring API to retrieve secrets instead of scraping kk output.",
        "Handle retrieved secrets in-memory and never log or display plaintext values.",
    ]
    print("\n".join(note_lines))
    print()
    print(header)
    print(f"{'Name':<40} {'Secret (masked)'}")
    print("-" * 80)
    for r in rows:
        name = r["name"]
        masked = mask_secret(r["secret"], cfg.mask_visible_ratio)
        print(f"{name:<40} {masked}")
