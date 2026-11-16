"""Supabase PostgreSQL 연결 관리."""
import os
from pathlib import Path
from threading import Lock
from typing import Generator

import psycopg
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
_pool = None
_pool_lock = Lock()


def connection_pool():
    """공통 풀만 사용하며 첫 DB 요청에서 연결을 준비한다."""
    global _pool
    with _pool_lock:
        if _pool is None:
            url = os.environ.get("DATABASE_URL", "").strip()
            if not url:
                raise RuntimeError("DATABASE_URL 환경변수를 설정해주세요.")
            _pool = ConnectionPool(
                url, min_size=1, max_size=8, timeout=5, open=False,
                kwargs={"connect_timeout": 5, "sslmode": "require", "row_factory": dict_row},
            )
            _pool.open()
        return _pool


def close_pool():
    global _pool
    with _pool_lock:
        if _pool is not None:
            _pool.close()
            _pool = None


def get_db() -> Generator[psycopg.Connection, None, None]:
    """요청 종료 시 커밋/롤백 후 연결을 반환한다. SET LOCAL/RLS도 초기화된다."""
    with connection_pool().connection() as connection:
        yield connection
