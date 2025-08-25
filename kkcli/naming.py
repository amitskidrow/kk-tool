import re
from typing import Tuple


NAME_RE = re.compile(r"^[A-Za-z0-9._:-]+/[A-Za-z0-9._:-]+$")


def normalize_pair(service: str, username: str) -> Tuple[str, str]:
    svc = service.strip().replace(" ", "_")
    usr = username.strip().replace(" ", "_")
    return svc, usr


def parse_name(name: str) -> Tuple[str, str]:
    if "/" not in name:
        raise ValueError("Name must be of form service/username")
    svc, usr = name.split("/", 1)
    svc, usr = normalize_pair(svc, usr)
    if not NAME_RE.match(f"{svc}/{usr}"):
        raise ValueError("Only A-Za-z0-9._:- and one '/' separator are allowed")
    return svc, usr


def label_for(service: str, username: str) -> str:
    return f"{service}/{username}"

