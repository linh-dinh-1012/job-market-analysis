from __future__ import annotations

import os
from dataclasses import dataclass


def _get_env(name: str, default: str | None = None) -> str | None:
    v = os.getenv(name)
    return v if (v is not None and v != "") else default


@dataclass(frozen=True)
class Settings:
    # -----------------------
    # Database (PostgreSQL)
    # -----------------------
    DB_HOST: str = _get_env("DB_HOST", "localhost") or "localhost"
    DB_PORT: int = int(_get_env("DB_PORT", "5432") or 5432)
    DB_NAME: str = _get_env("DB_NAME", "job_market_analysis")
    DB_USER: str = _get_env("DB_USER", "job_app") 
    DB_PASSWORD: str = _get_env("DB_PASSWORD", "123456")
    DATABASE_URL: str | None = _get_env("DATABASE_URL", None)

    # -----------------------
    # France Travail API
    # -----------------------
    FT_CLIENT_ID: str | None = _get_env("FT_CLIENT_ID", None)
    FT_CLIENT_SECRET: str | None = _get_env("FT_CLIENT_SECRET", None)

    # -----------------------
    # Ingestion params (FT)
    # -----------------------
    FT_STEP: int = int(_get_env("FT_STEP", "150") or 150)
    FT_MAX_RESULTS: int = int(_get_env("FT_MAX_RESULTS", "300") or 300)

    # -----------------------
    # General
    # -----------------------
    LOG_LEVEL: str = _get_env("LOG_LEVEL", "INFO") or "INFO"


settings = Settings()