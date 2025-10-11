from dataclasses import dataclass


@dataclass
class Config:
    namespace: str = "ss"
    store_mode: str = "attribute"  # or "collection"
    default_env: str = "dev"
    mask_visible_ratio: float = 0.35

    @property
    def context_header(self) -> str:
        return (
            f"ns={self.namespace} (fixed), mode={self.store_mode}, "
            f"env={self.default_env} (fixed) — use service/username labels."
        )


def load_config() -> Config:
    """
    Return fixed configuration used by the kk CLI.

    Namespace and environment are intentionally immutable to keep
    the tool predictable for automated agents.
    """
    return Config()
