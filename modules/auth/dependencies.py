"""사용자별 데이터를 가져오기위한 함수"""
from typing import Annotated

from fastapi import Depends, Request

from modules.auth.auth_store import User, authenticated


def get_current_user(request: Request) -> User:
    user, _access_token = authenticated(request)
    return User(**user)

CurrentUser = Annotated[User, Depends(get_current_user)]