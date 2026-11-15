"""
TERRA-X Environment Configuration & .env Loader
Loads environment variables from .env if present.
"""

import os
from pathlib import Path

def load_env_file(env_path: Path = None):
    """Loads key-value pairs from .env into os.environ."""
    if env_path is None:
        env_path = Path(__file__).resolve().parent.parent / ".env"
    
    if not env_path.exists():
        return
    
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception as e:
        pass

# Auto-load on import
load_env_file()

