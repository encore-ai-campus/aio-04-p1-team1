from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from psycopg import Connection
from uuid import UUID

from modules.jd_match.model import JobPosting, Profile
from modules.jd_match.service import get_jd_match_score, get_job_posting, get_profile
from modules.auth import auth_store
from shared.components.compass import apply_member_shell
from shared.auth_dependencies import CurrentUser
from shared.database import get_db

router = APIRouter(prefix="/jd_match", tags=["jd_match"])
TEMPLATE_PATH = Path(__file__).with_name("templates") / "match.html"
START_TEMPLATE_PATH = Path(__file__).with_name("templates") / "start.html"


def page_user(request: Request):
    try:
        return auth_store.me(request)
    except HTTPException as exc:
        if exc.status_code == 401:
            return RedirectResponse("/signin", status_code=303)
        raise


def render_match_page(user):
    page = TEMPLATE_PATH.read_text(encoding="utf-8")
    return apply_member_shell(page, user, current="jd_match")


def render_start_page(user):
    page = START_TEMPLATE_PATH.read_text(encoding="utf-8")
    return apply_member_shell(page, user, current="jd_match")


@router.get("", response_class=HTMLResponse)
def match_page(request: Request):
    user = page_user(request)
    return user if isinstance(user, RedirectResponse) else HTMLResponse(render_start_page(user))


@router.get("/profile", response_model=Profile | None)
def profile(
    user: CurrentUser,
    db: Annotated[Connection, Depends(get_db)],
):
    return get_profile(db, user.email, user.id)


@router.get("/job-postings/{job_posting_id}", response_model=JobPosting)
def job_posting(
    job_posting_id: UUID,
    db: Annotated[Connection, Depends(get_db)],
):
    result = get_job_posting(db, job_posting_id)
    if result is None:
        raise HTTPException(status_code=404, detail="공고를 찾을 수 없습니다.")
    return result


@router.get("/job-postings/{job_posting_id}/score")
def job_posting_score(
    job_posting_id: UUID,
    user: CurrentUser,
    db: Annotated[Connection, Depends(get_db)],
):
    return get_jd_match_score(db, user.id, job_posting_id, user.email)


@router.get("/my-data")
def get_my_data(user: CurrentUser):
    return {"user_id": str(user.id)}


@router.get("/{job_posting_id}", response_class=HTMLResponse)
def match_page_for_job(job_posting_id: UUID, request: Request):
    user = page_user(request)
    return user if isinstance(user, RedirectResponse) else HTMLResponse(render_match_page(user))

# 공고 상세 라우팅
