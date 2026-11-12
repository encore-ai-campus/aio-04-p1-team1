"""로그인한 회원의 메인 화면 라우터."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from modules.main.page import render_main
from shared.auth_dependencies import get_current_user

router = APIRouter(tags=["메인"])


@router.get("/main", response_class=HTMLResponse, summary="메인 화면")
def main_page(request: Request):
    try:
        user = get_current_user(request)
    except HTTPException as exc:
        if exc.status_code == 401:
            return RedirectResponse("/signin", status_code=303)
        raise
    return render_main(user.model_dump())
