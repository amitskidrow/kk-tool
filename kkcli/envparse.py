from pathlib import Path
from typing import Dict


def parse_env_file(path: Path) -> Dict[str, str]:
    secrets: Dict[str, str] = {}
    with path.open('r') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            k, v = k.strip(), v.strip()
            if v.startswith('"') and v.endswith('"') and len(v) >= 2:
                v = v[1:-1]
            elif v.startswith("'") and v.endswith("'") and len(v) >= 2:
                v = v[1:-1]
            if k:
                secrets[k] = v
    return secrets


def extract_service_name(filename: str) -> str:
    name = filename
    if name.startswith('.'):
        name = name[1:]
    if name.endswith('.env'):
        name = name[:-4]
    return name

