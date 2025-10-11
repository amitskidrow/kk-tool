import sys
from argparse import SUPPRESS

from ..context import get_context
from ..masking import mask_secret
from ..naming import parse_name
from ..output import result_payload
from ..storage import get as get_item

_PASS_PHRASE = "ss"


def register(subparsers):
    p = subparsers.add_parser(
        "get",
        help="Get a secret from namespace 'ss' (masked output by default).",
    )
    p.add_argument("name", help="service/username")
    p.add_argument("--pass", dest="passphrase", default=None, help=SUPPRESS)
    p.add_argument("--json", action="store_true", help="Return machine-readable output.")
    p.set_defaults(func=run)


def run(args):
    ctx = get_context()
    cfg = ctx.config
    header = f"[{cfg.context_header}]"
    if not args.json:
        print(header)
    svc, usr = parse_name(args.name)
    store = ctx.store
    val = get_item(store, svc, usr)
    if val is None:
        message = "Not found"
        if args.json:
            print(
                result_payload(
                    cfg,
                    {
                        "status": "error",
                        "error": message,
                        "name": f"{svc}/{usr}",
                    },
                )
            )
        else:
            print(message, file=sys.stderr)
        sys.exit(1)
    full_secret = val
    masked = mask_secret(full_secret, cfg.mask_visible_ratio)
    reveal = args.passphrase == _PASS_PHRASE if args.passphrase is not None else False
    if args.json:
        print(
            result_payload(
                cfg,
                {
                    "status": "ok",
                    "name": f"{svc}/{usr}",
                    "secret": full_secret if reveal else masked,
                    "masked": not reveal,
                },
            )
        )
        return
    output = full_secret if reveal else masked
    print(output)
