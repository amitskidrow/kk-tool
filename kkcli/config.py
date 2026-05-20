import os
import sys
from dataclasses import dataclass
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


@dataclass
class Config:
    namespace: str = "ss"
    store_mode: str = "attribute"  # or "collection"
    default_env: str = "dev"
    mask_visible_ratio: float = 0.35

    @property
    def context_header(self) -> str:
        return (
            f"ns={self.namespace}, mode={self.store_mode}, "
            f"env={self.default_env} — use service/username labels."
        )


def load_config() -> Config:
    """
    Load configuration with precedence:
    Default values < Config file (config.toml) < Environment variables
    """
    config = Config()

    # 1. Load from file
    config_dir = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "kk"
    config_file = config_dir / "config.toml"
    
    file_config = {}
    if config_file.exists() and tomllib is not None:
        try:
            with config_file.open("rb") as f:
                file_config = tomllib.load(f)
        except Exception:
            pass  # Silent fallback on invalid TOML

    # Apply file configuration
    if "namespace" in file_config:
        config.namespace = str(file_config["namespace"])
    if "store_mode" in file_config:
        config.store_mode = str(file_config["store_mode"])
    if "default_env" in file_config:
        config.default_env = str(file_config["default_env"])
    if "mask_visible_ratio" in file_config:
        try:
            config.mask_visible_ratio = float(file_config["mask_visible_ratio"])
        except ValueError:
            pass

    # 2. Load from environment variables
    if os.environ.get("KK_NAMESPACE"):
        config.namespace = os.environ["KK_NAMESPACE"]
    if os.environ.get("KK_STORE_MODE"):
        config.store_mode = os.environ["KK_STORE_MODE"]
    if os.environ.get("KK_DEFAULT_ENV"):
        config.default_env = os.environ["KK_DEFAULT_ENV"]
    if os.environ.get("KK_MASK_VISIBLE_RATIO"):
        try:
            config.mask_visible_ratio = float(os.environ["KK_MASK_VISIBLE_RATIO"])
        except ValueError:
            pass

    return config

