"""로그인 화면 라우터."""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from modules.auth.auth_ui import render_auth

router = APIRouter(tags=["회원 화면"])


@router.get("/signin", response_class=HTMLResponse, summary="로그인 페이지")
def signin_page(request: Request):
    return render_auth("signin", getattr(request.app.state, "main_path", None))
