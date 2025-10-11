import argparse
from ..context import get_context
from ..output import masked_items_payload, print_masked_table
from ..storage import list_items


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
    ctx = get_context()
    cfg = ctx.config
    header = f"[{cfg.context_header}]"
    store = ctx.store
    rows = list_items(store, contains=args.contains, env=None)
    if args.json:
        print(masked_items_payload(cfg, rows))
        return
    note_lines = [
        "NOTE: Masked output is provided for manual inspection only.",
        "Agents must call the Secret Service/keyring API to retrieve secrets instead of scraping kk output.",
        "Handle retrieved secrets in-memory and never log or display plaintext values.",
    ]
    print("\n".join(note_lines))
    print()
    print(header)
    print_masked_table(cfg, rows)
