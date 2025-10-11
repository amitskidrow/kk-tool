import json
import sys
from argparse import SUPPRESS

from ..config import load_config
from ..masking import mask_secret
from ..naming import parse_name
from ..storage import get as get_item, open_store

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
    cfg = load_config()
    header = f"[{cfg.context_header}]"
    if not args.json:
        print(header)
    svc, usr = parse_name(args.name)
    store = open_store(cfg.namespace, cfg.store_mode)
    val = get_item(store, svc, usr)
    if val is None:
        message = "Not found"
        if args.json:
            print(
                json.dumps(
                    {
                        "context": {
                            "namespace": cfg.namespace,
                            "env": cfg.default_env,
                            "store_mode": cfg.store_mode,
                        },
                        "result": {
                            "status": "error",
                            "error": message,
                            "name": f"{svc}/{usr}",
                        },
                    }
                )
            )
        else:
            print(message, file=sys.stderr)
        sys.exit(1)
    full_secret = val
    masked = mask_secret(full_secret, cfg.mask_visible_ratio)
    reveal = args.passphrase == _PASS_PHRASE if args.passphrase is not None else False
    if args.json:
        payload = {
            "context": {
                "namespace": cfg.namespace,
                "env": cfg.default_env,
                "store_mode": cfg.store_mode,
            },
            "result": {
                "status": "ok",
                "name": f"{svc}/{usr}",
                "secret": full_secret if reveal else masked,
                "masked": not reveal,
            },
        }
        print(json.dumps(payload))
        return
    output = full_secret if reveal else masked
    print(output)
