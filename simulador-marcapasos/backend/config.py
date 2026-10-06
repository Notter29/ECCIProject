"""Environment-backed configuration for local and deployed environments."""
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./marcapasos.db")
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "5"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or secrets.token_urlsafe(32)
CORS_ORIGINS = tuple(
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:4200,http://127.0.0.1:4200",
    ).split(",")
    if origin.strip()
)
NOAH_LLM_BASE_URL = os.getenv("NOAH_LLM_BASE_URL", "").rstrip("/")
NOAH_LLM_API_KEY = os.getenv("NOAH_LLM_API_KEY", "")
NOAH_LLM_MODEL = os.getenv("NOAH_LLM_MODEL", "")
NOAH_MAX_CONCURRENT_REQUESTS = max(1, int(os.getenv("NOAH_MAX_CONCURRENT_REQUESTS", "8")))