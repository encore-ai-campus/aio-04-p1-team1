"""Supabase PostgreSQL 연결 관리."""

import os
from pathlib import Path
from typing import Generator

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row


load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)


def get_db() -> Generator[psycopg.Connection, None, None]:
    """FastAPI Depends용 연결. 성공 시 커밋, 예외 시 롤백 후 닫는다."""
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if not database_url:
        raise RuntimeError("DATABASE_URL 환경변수를 설정해주세요.")

    with psycopg.connect(
        database_url,
        connect_timeout=5,
        sslmode="require",
        row_factory=dict_row, # vs code 경고
    ) as connection:
        yield connection
