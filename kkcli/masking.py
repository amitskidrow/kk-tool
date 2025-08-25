from typing import Union


def mask_secret(secret: Union[str, bytes], visible_ratio: float = 0.35, min_visible: int = 3) -> str:
    if isinstance(secret, bytes):
        try:
            secret = secret.decode()
        except Exception:
            secret = secret.decode(errors="ignore")
    s = secret or ""
    if not s:
        return ""
    if len(s) == 1:
        return "*"
    n = max(min_visible, int(len(s) * visible_ratio))
    n = min(n, len(s) - 1)
    return s[:n] + ("*" * (len(s) - n))

