import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # study-platform/

# Paths default to the repo layout, but can be overridden via environment
# variables (used by the Docker setup to mount content read-only and persist
# the SQLite DB on a named volume). Defaults are unchanged when unset.
CONTENT_DIR = Path(os.environ.get("CONTENT_DIR") or BASE_DIR / "content")
DB_PATH = Path(os.environ.get("DB_PATH") or BASE_DIR / "backend" / "progress.db")
