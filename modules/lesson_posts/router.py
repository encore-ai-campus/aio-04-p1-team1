from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from modules.jd_match.page import render_match_page

router = APIRouter(prefix="/job_posts", tags=["job_posts"])


@router.get("", response_class=HTMLResponse)
@router.get("/preview", response_class=HTMLResponse)
def job_detail_preview():
    return HTMLResponse(render_match_page())
