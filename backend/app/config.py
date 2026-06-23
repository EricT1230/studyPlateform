from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # study-platform/
CONTENT_DIR = BASE_DIR / "content"
DB_PATH = BASE_DIR / "backend" / "progress.db"
