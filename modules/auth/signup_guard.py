"""가입 전 이메일 존재 확인과 같은 이메일의 동시 가입 요청 제어."""

from contextlib import contextmanager, suppress
import os
from pathlib import Path
import ssl
from urllib.parse import unquote, urlsplit

from fastapi import HTTPException

DUPLICATE_EMAIL_MESSAGE = "이미 가입된 이메일입니다."
CHECK_FAILED_MESSAGE = "회원가입 정보를 확인하지 못했습니다. 잠시 후 다시 시도해 주세요."
SIGNUP_IN_PROGRESS_MESSAGE = "해당 이메일의 회원가입을 처리 중입니다. 잠시 후 다시 시도해 주세요."


def _connect():
    # 이 조회는 서버에서만 수행합니다. 로그인·일반 회원 데이터 API와 분리합니다.
    import certifi
    import pg8000.dbapi

    url = urlsplit(os.environ.get("DATABASE_URL", "").strip())
    if url.scheme not in {"postgres", "postgresql"} or not url.hostname or not url.username:
        raise ValueError("Server database configuration is missing")
    tls = ssl.create_default_context(cafile=certifi.where())
    ca_path = Path(os.environ.get("SUPABASE_DB_CA_FILE", "") or Path(__file__).with_name("supabase-ca.crt"))
    if ca_path.is_file():
        tls.load_verify_locations(cafile=str(ca_path))
    return pg8000.dbapi.connect(
        user=unquote(url.username or ""),
        password=unquote(url.password or ""),
        host=url.hostname,
        port=url.port or 5432,
        database=unquote(url.path.lstrip("/")) or "postgres",
        ssl_context=tls,
        timeout=5,
    )


@contextmanager
def signup_guard(email):
    """가입 API를 호출하는 동안 동일 이메일의 트랜잭션 잠금을 유지합니다.

    기존 회원 여부는 인증 완료 상태와 무관하게 확인합니다. 회원 데이터에는
    쓰지 않으며, 종료 시 롤백과 연결 종료로 잠금을 해제합니다.
    """
    connection = None
    try:
        connection = _connect()
        cursor = connection.cursor()
        cursor.execute("SET LOCAL statement_timeout = '5s'")
        cursor.execute(
            "SELECT pg_catalog.pg_try_advisory_xact_lock(pg_catalog.hashtextextended(%s, 73419027))",
            (email.strip().lower(),),
        )
        acquired = cursor.fetchone()[0]
        cursor.execute(
            "SELECT EXISTS (SELECT 1 FROM auth.users WHERE lower(email) = %s)",
            (email.strip().lower(),),
        )
        if cursor.fetchone()[0]:
            raise HTTPException(status_code=409, detail=DUPLICATE_EMAIL_MESSAGE)
        if not acquired:
            raise HTTPException(status_code=409, detail=SIGNUP_IN_PROGRESS_MESSAGE)
        yield
    except HTTPException:
        raise
    except Exception:
        # DB 연결 정보나 입력 이메일을 오류 응답에 포함하지 않습니다.
        raise HTTPException(status_code=503, detail=CHECK_FAILED_MESSAGE) from None
    finally:
        if connection is not None:
            with suppress(Exception):
                connection.rollback()
            with suppress(Exception):
                connection.close()
