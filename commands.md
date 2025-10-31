pipx install --force git+https://github.com/amitskidrow/kk-tool@main

## New: `kk code <selector>`

Show a Python snippet using python-keyring to retrieve one or more credentials by index or label.

Examples:

```bash
kk list
kk code 1
kk code anthropic/ANTHROPIC_API_KEY
kk code 3,4 --json
kk code nats/NATS_URL --quiet
kk code redis/REDIS_URL --emit-markers
```
