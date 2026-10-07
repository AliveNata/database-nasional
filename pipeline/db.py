"""Koneksi Postgres. DATABASE_URL dibaca dari environment atau file .env."""
from __future__ import annotations

import os
from pathlib import Path

import psycopg

_ENV = Path(__file__).resolve().parent.parent / ".env"


def _load_dotenv() -> None:
    if not _ENV.exists():
        return
    for line in _ENV.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def get_dsn() -> str:
    _load_dotenv()
    dsn = os.environ.get("DATABASE_URL")
    if not dsn:
        raise SystemExit("DATABASE_URL belum diset (isi di .env atau export dulu)")
    return dsn


def connect() -> psycopg.Connection:
    return psycopg.connect(get_dsn())
