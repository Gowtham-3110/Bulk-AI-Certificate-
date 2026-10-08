import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

APP_NAME = os.getenv("APP_NAME", "Bulk Certificate Generator")
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'certificates.db'}")
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", BASE_DIR / "certificates_storage"))

DEFAULT_ISSUER = os.getenv("DEFAULT_ISSUER", "Global Certification Authority")

# Ensure storage directory exists
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
