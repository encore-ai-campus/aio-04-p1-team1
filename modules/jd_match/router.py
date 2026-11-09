from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from psycopg import Connection
from uuid import UUID

from modules.jd_match.model import JobPosting, Profile
from modules.jd_match.service import get_jd_match_score, get_job_posting, get_profile
from shared.components.header import render_header
from shared.auth_dependencies import CurrentUser
from shared.database import get_db

router = APIRouter(prefix="/jd_match", tags=["jd_match"])
TEMPLATE_PATH = Path(__file__).with_name("templates") / "match.html"


def render_match_page():
    page = TEMPLATE_PATH.read_text(encoding="utf-8")
    return page.replace("__HEADER__", render_header(member=True))


@router.get("", response_class=HTMLResponse)
def match_page():
    return HTMLResponse(render_match_page())


@router.get("/profile", response_model=Profile | None)
def profile(
    user: CurrentUser,
    db: Annotated[Connection, Depends(get_db)],
):
    return get_profile(db, user.id)


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
    return get_jd_match_score(db, user.id, job_posting_id)


@router.get("/my-data")
def get_my_data(user: CurrentUser):
    return {"user_id": str(user.id)}


@router.get("/{job_posting_id}", response_class=HTMLResponse)
def match_page_for_job(job_posting_id: UUID):
    return HTMLResponse(render_match_page())

# 공고 상세 라우팅
