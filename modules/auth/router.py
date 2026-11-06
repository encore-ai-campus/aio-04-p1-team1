from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse

from modules.auth.auth_store import (
    ProfileUpdate,
    SigninRequest,
    SignupRequest,
    User,
    me as get_current_user,
    signin as authenticate,
    signout as end_session,
    signup as create_account,
    update_profile as change_profile,
)

router = APIRouter(prefix="/api/auth", tags=["회원 인증"])
callback_router = APIRouter(tags=["회원 인증"])


@callback_router.get("/auth/confirmed", response_class=HTMLResponse, include_in_schema=False)
def email_confirmed():
    return HTMLResponse("""<!doctype html><html lang="ko"><meta charset="utf-8"><title>이메일 인증</title>
    <p>인증 결과를 확인하고 로그인 화면으로 이동합니다.</p>
    <script>const error=new URLSearchParams(location.hash.slice(1)).has('error')||new URLSearchParams(location.search).has('error');
    history.replaceState(null,'','/auth/confirmed');location.replace(error?'/signin?confirmation_error=1':'/signin?confirmed=1');</script>
    <noscript>이메일 인증 결과를 확인한 후 <a href="/signin">로그인</a>해 주세요.</noscript></html>""",
    headers={"Referrer-Policy": "no-referrer"})


@router.post("/signup", status_code=202, summary="회원가입 및 인증 메일 요청")
def signup(body: SignupRequest):
    return create_account(body)


@router.post("/signin", response_model=User, summary="로그인")
def signin(body: SigninRequest, request: Request, response: Response):
    return authenticate(body, request, response)


@router.get("/me", response_model=User, summary="현재 로그인한 회원")
def me(request: Request):
    return get_current_user(request)


@router.post("/signout", status_code=204, summary="로그아웃")
def signout(request: Request, response: Response):
    return end_session(request, response)


@router.patch("/me", response_model=User, summary="내 표시 이름 수정")
def update_profile(body: ProfileUpdate, request: Request):
    return change_profile(body, request)
