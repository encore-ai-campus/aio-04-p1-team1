"""현재 회원의 비밀번호를 재검증한 후 Supabase Auth 비밀번호 변경."""
from fastapi import HTTPException


def change_password(user, current_password, new_password, auth_request):
    try:
        session=auth_request('POST','/auth/v1/token',params={'grant_type':'password'},
                             json={'email':user['email'],'password':current_password})
    except HTTPException as exc:
        if exc.status_code in {401,403}:
            raise HTTPException(status_code=400,detail='이전 비밀번호가 올바르지 않습니다.') from None
        raise
    token=session.get('access_token') if isinstance(session,dict) else None
    if not token:
        raise HTTPException(status_code=503,detail='비밀번호 확인 응답을 확인하지 못했습니다.')
    changed=False
    try:
        verified=auth_request('GET','/auth/v1/user',token=token)
        if not isinstance(verified,dict) or str(verified.get('id'))!=str(user['id']):
            raise HTTPException(status_code=403,detail='현재 로그인한 회원의 비밀번호를 입력해 주세요.')
        auth_request('PUT','/auth/v1/user',token=token,
                     json={'password':new_password,'current_password':current_password})
        changed=True
    finally:
        try:
            auth_request('POST','/auth/v1/logout',token=token,params={'scope':'local'})
        except HTTPException:
            # 이미 변경한 비밀번호를 정리 요청 실패 때문에 미변경으로 안내하지 않습니다.
            if not changed:
                raise
