"""로그인한 회원의 메인 화면 라우터."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from psycopg import Connection, Error
from fastapi.responses import HTMLResponse, RedirectResponse

from modules.main.page import render_main
from shared.auth_dependencies import get_current_user, CurrentUser
from shared.database import get_db
from modules.job_posts.job_repository import get_home_jobs
from modules.job_posts.search_models import JobResults

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


@router.get('/main/api/jobs', response_model=JobResults, summary='희망 직무 우선 메인 공고 6개')
def home_jobs(user: CurrentUser, db: Annotated[Connection, Depends(get_db)]):
    try:
        return get_home_jobs(db, user.id)
    except Error:
        raise HTTPException(503, '공고를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.') from None
