"""공통 DB 연결과 회원별 RLS를 이용한 profiles 개인정보 조회·수정."""
from contextlib import contextmanager
import json
from uuid import UUID

from fastapi import HTTPException
from psycopg import Error
from shared.database import get_db


@contextmanager
def member_cursor(user_id):
    identifier = UUID(str(user_id))
    try:
        with contextmanager(get_db)() as db, db.cursor() as cursor:
            cursor.execute('SET LOCAL ROLE authenticated')
            cursor.execute(
                "SELECT set_config('request.jwt.claims',%s,true), "
                "set_config('request.jwt.claim.sub',%s,true)",
                (json.dumps({'sub':str(identifier),'role':'authenticated'}),str(identifier)),
            )
            yield cursor, identifier
    except Error:
        raise HTTPException(503, '회원정보를 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.') from None


def get_profile(user_id):
    with member_cursor(user_id) as (cursor, identifier):
        cursor.execute(
            'SELECT user_id,name,email,use_yn FROM public.profiles WHERE user_id=%s',
            (identifier,),
        )
        return cursor.fetchone()


def update_name(user_id, name):
    with member_cursor(user_id) as (cursor, identifier):
        cursor.execute(
            'UPDATE public.profiles SET name=%s WHERE user_id=%s AND use_yn=\'Y\' RETURNING user_id,name,email',
            (name,identifier),
        )
        return cursor.fetchone()


def deactivate(user_id):
    """비밀번호 검증 후 서버에서만 본인 계정을 비활성화합니다."""
    identifier = UUID(str(user_id))
    try:
        # 상태 변경은 서버 권한으로만 수행하며 클라이언트가 회원 ID를 지정하지 않습니다.
        with contextmanager(get_db)() as db, db.cursor() as cursor:
            cursor.execute(
                "UPDATE public.profiles SET use_yn='N' WHERE user_id=%s AND use_yn='Y' RETURNING user_id",
                (identifier,),
            )
            return cursor.fetchone() is not None
    except Error:
        raise HTTPException(503, '탈퇴 처리에 실패했습니다. 잠시 후 다시 시도해 주세요.') from None
