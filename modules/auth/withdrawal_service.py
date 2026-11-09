"""회원 탈퇴 전 비밀번호 확인과 추후 삭제 처리 연결 지점."""

from fastapi import HTTPException


def verify_password(user, password, auth_request):
    """현재 로그인한 회원의 비밀번호만 확인하고 확인용 세션은 종료합니다."""
    try:
        session = auth_request(
            "POST", "/auth/v1/token", params={"grant_type": "password"},
            json={"email": user["email"], "password": password},
        )
    except HTTPException as exc:
        if exc.status_code in {401, 403}:
            raise HTTPException(status_code=400, detail="비밀번호가 올바르지 않습니다.") from None
        raise
    token = session.get("access_token") if isinstance(session, dict) else None
    if not token:
        raise HTTPException(status_code=503, detail="비밀번호 확인 응답을 확인하지 못했습니다.")
    try:
        verified_user = auth_request("GET", "/auth/v1/user", token=token)
        if str(verified_user.get("id")) != str(user["id"]):
            raise HTTPException(status_code=403, detail="현재 로그인한 회원의 비밀번호를 입력해 주세요.")
    finally:
        # 확인 과정에서 만든 세션만 정리합니다. 기존 브라우저 로그인은 유지합니다.
        auth_request("POST", "/auth/v1/logout", token=token, params={"scope": "local"})


def complete_withdrawal(user_id: str) -> bool:
    """확정된 데이터 정리 및 Supabase 계정 삭제 처리를 나중에 연결합니다.

    현재는 삭제를 수행하지 않고 False를 반환합니다. 실제 구현 시 서버에서
    모든 삭제가 완료된 경우에만 True를 반환해야 합니다. 비밀번호는 전달하지
    않습니다. 이 함수만 따로 호출하는 외부 API는 제공하지 않습니다.
    """
    return False
