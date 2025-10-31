import argparse
from typing import List, Tuple

from ..context import get_context
from ..naming import parse_name
from ..output import result_payload
from ..storage import list_items

BANNER_LINES = [
    "This CLI shows masked secrets from your system keyring (Secret Service).",
    "Automations should fetch values directly via python-keyring; do not scrape kk output.",
    "",
    "DO:",
    "- Use keyring.get_password(<service>, <username>) to retrieve secrets.",
    "- Keep secrets in-memory and redact/mask logs.",
    "DON'T:",
    "- Print plaintext secrets or rely on kk's masked output in code.",
    "",
    "Install/run tips:",
    "- uv (ephemeral): uv run --with keyring --with secretstorage python -c \"import keyring; print(keyring.get_password('nats','NATS_URL'))\"",
    "- pip: pip install keyring secretstorage",
]

_DEF_HEADING = "Python example (python-keyring):"
_DEF_SNIPPET_LINE = "print(keyring.get_password('{svc}', '{usr}'))"
_DEF_IMPORT = "import keyring"
_DEF_MARKERS = ("<<<BEGIN_DESCRIPTION>>>", "<<<END_DESCRIPTION>>>", "<<<BEGIN_CODE:python>>>", "<<<END_CODE>>>")
_DEF_BANNER = "\n" + "\n".join(BANNER_LINES) + "\n"
_DEF_MD_HEADING = "## Keyring usage guidance"
_DEF_MD_CODE_HEADING = "### Python example (python-keyring)"
_DEF_ERR_RANGE = "Error: index {n} is out of range (1..{N})"
_DEF_ERR_LABEL = "Error: credential '{label}' not found"
_DEF_EMPTY = "No credentials found. Use your existing setup/ingest flow, then re-run."
_DEF_JSON_BANNER = {"purpose": BANNER_LINES[0], "automation_note": BANNER_LINES[1], "do": [BANNER_LINES[4], BANNER_LINES[5]], "dont": [BANNER_LINES[7]], "tips": [BANNER_LINES[10], BANNER_LINES[11]]}
_DEF_LANG = "python"

# --- argparse registration ----------------------------------------------------


def register(subparsers):
    p = subparsers.add_parser(
        "code",
        help="Show a Python snippet using python-keyring for selected credential(s).",
        description=(
            "Emit a minimal Python code block that fetches the selected credential(s) by index or label."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("selector", help="Index from `kk list` (1-based) or label service/username.")
    p.add_argument("--multi", default=None, help="Comma-separated selectors.")
    p.add_argument("--json", action="store_true", help="Emit JSON payload.")
    p.add_argument("--quiet", "-q", action="store_true", help="Snippet only.")
    p.add_argument("--md", action="store_true", help="Render with Markdown headings.")
    p.add_argument("--emit-markers", action="store_true", help="Wrap description and code in BEGIN/END markers.")
    p.add_argument("--agent", action="store_true", help="Alias for --quiet --emit-markers.")
    p.set_defaults(func=run)


# --- helpers ------------------------------------------------------------------


def _enumerate_sorted():
    ctx = get_context()
    rows = list_items(ctx.store)
    return ctx, rows


def _resolve_selector(selector: str, rows) -> Tuple[str, str]:
    # int index?
    try:
        n = int(selector)
        if n < 1 or n > len(rows):
            raise IndexError
        r = rows[n - 1]
        svc = r.attrs.get("service", "")
        usr = r.attrs.get("username", "")
        return svc, usr
    except ValueError:
        # label
        svc, usr = parse_name(selector)
        for r in rows:
            if r.attrs.get("service") == svc and r.attrs.get("username") == usr:
                return svc, usr
        raise KeyError(selector)


def _render_snippet(pairs: List[Tuple[str, str]]) -> str:
    lines = [_DEF_IMPORT]
    for svc, usr in pairs:
        lines.append(_DEF_SNIPPET_LINE.format(svc=svc, usr=usr))
    return "\n".join(lines) + "\n"

def _print_banner():
    print(_DEF_BANNER, end="")


def _print_human(snippet: str, *, with_banner: bool, md: bool, markers: bool):
    begin_desc, end_desc, begin_code, end_code = _DEF_MARKERS
    if markers:
        print(begin_desc)
    if with_banner:
        if md:
            print(_DEF_MD_HEADING)
        _print_banner()
    if markers:
        print(end_desc)
    if md and with_banner:
        print()
        print(_DEF_MD_CODE_HEADING)
    if markers:
        print(begin_code)
    if md:
        print("```python")
    print(snippet, end="")
    if md:
        print("```")
    if markers:
        print(end_code)


def _print_json(ctx, items: List[Tuple[str, str]], snippet: str):
    if len(items) == 1:
        svc, usr = items[0]
        obj = {
            "service": svc,
            "username": usr,
            "language": _DEF_LANG,
            "snippet": snippet,
            "banner": _DEF_JSON_BANNER,
        }
    else:
        obj = {
            "items": [
                {
                    "service": s,
                    "username": u,
                    "language": _DEF_LANG,
                    "snippet": _render_snippet([(s, u)]),
                }
                for s, u in items
            ]
        }
    print(result_payload(ctx.config, obj))

# --- command entry ------------------------------------------------------------


def run(args):
    ctx, rows = _enumerate_sorted()
    if not rows:
        if args.json:
            print(result_payload(ctx.config, {"error": _DEF_EMPTY}))
            return 1
        print(_DEF_EMPTY)
        return 1

    selectors: List[str] = []
    if args.multi:
        selectors.extend([s.strip() for s in args.multi.split(",") if s.strip()])
    selectors.append(args.selector)

    pairs: List[Tuple[str, str]] = []
    errors: List[str] = []

    for sel in selectors:
        try:
            svc, usr = _resolve_selector(sel, rows)
            pairs.append((svc, usr))
        except IndexError:
            errors.append(_DEF_ERR_RANGE.format(n=sel, N=len(rows)))
        except (KeyError, ValueError):
            errors.append(_DEF_ERR_LABEL.format(label=sel))

    if errors:
        if args.json:
            print(result_payload(ctx.config, {"error": "; ".join(errors)}))
        else:
            for e in errors:
                print(e)
        return 1

    snippet = _render_snippet(pairs)

    if args.agent:
        args.quiet = True
        args.emit_markers = True

    if args.json:
        _print_json(ctx, pairs, snippet if len(pairs) == 1 else "")
        return

    _print_human(snippet, with_banner=not args.quiet, md=args.md, markers=args.emit_markers)
