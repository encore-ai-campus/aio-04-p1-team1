"""가입 전 이메일 존재 확인과 같은 이메일의 동시 가입 요청 제어."""

from contextlib import contextmanager

from fastapi import HTTPException
from shared.database import get_db

DUPLICATE_EMAIL_MESSAGE = "이미 가입된 이메일입니다."
CHECK_FAILED_MESSAGE = "회원가입 정보를 확인하지 못했습니다. 잠시 후 다시 시도해 주세요."
SIGNUP_IN_PROGRESS_MESSAGE = "해당 이메일의 회원가입을 처리 중입니다. 잠시 후 다시 시도해 주세요."


@contextmanager
def signup_guard(email):
    """공통 DB 연결로 가입 요청 동안 동일 이메일의 트랜잭션 잠금을 유지합니다.

    인증 완료 상태와 무관하게 기존 회원을 확인합니다. 회원 데이터에는 쓰지
    않으며, 종료 시 롤백으로 잠금을 해제하고 공통 연결을 닫습니다.
    """
    try:
        with contextmanager(get_db)() as connection:
            with connection.transaction(force_rollback=True), connection.cursor() as cursor:
                cursor.execute("SET LOCAL statement_timeout = '5s'")
                cursor.execute(
                    "SELECT pg_catalog.pg_try_advisory_xact_lock(pg_catalog.hashtextextended(%s, 73419027)) AS acquired",
                    (email.strip().lower(),),
                )
                acquired = cursor.fetchone()["acquired"]
                cursor.execute(
                    "SELECT EXISTS (SELECT 1 FROM auth.users WHERE lower(email) = %s) AS email_exists",
                    (email.strip().lower(),),
                )
                if cursor.fetchone()["email_exists"]:
                    raise HTTPException(status_code=409, detail=DUPLICATE_EMAIL_MESSAGE)
                if not acquired:
                    raise HTTPException(status_code=409, detail=SIGNUP_IN_PROGRESS_MESSAGE)
                yield
    except HTTPException:
        raise
    except Exception:
        # DB 연결 정보나 입력 이메일을 오류 응답에 포함하지 않습니다.
        raise HTTPException(status_code=503, detail=CHECK_FAILED_MESSAGE) from None
