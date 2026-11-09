"""
공통 FastAPI 인증 의존성

사용예시: 현재 로그인한 사용자 ID 가져오기 

from shared.auth_dependencies import CurrentUser

@router.get("/my-data")
def get_my_data(user: CurrentUser):
    return {"user_id": str(user.id)}


"""

from typing import Annotated
from fastapi import Depends, Request
from pydantic import BaseModel
from uuid import UUID

class User(BaseModel):
    id: UUID
    name: str
    email: str
    # 필요 시 필드 추가

def get_current_user(request: Request) -> User:
    """현재 로그인한 사용자 정보를 반환합니다."""
    from modules.auth.auth_store import authenticated

    user, _access_token = authenticated(request)
    return User(**user)


CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]
