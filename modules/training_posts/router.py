import json
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from shared.auth_dependencies import get_current_user
from modules.training_posts.page import PAGE, render_training_page
from modules.training_posts.repository import CatalogueStorageError
from modules.training_posts.service import CATEGORIES, catalogue_data, escape
router = APIRouter(prefix="/training_posts", tags=["교육목록"])

@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def page(request: Request, start: date | None = None, end: date | None = None, data: bool = False):
    today = datetime.now(timezone(timedelta(hours=9))).date()
    start = start or today - timedelta(days=365)
    end = end or today + timedelta(days=365)
    if start > end:
        return HTMLResponse("조회 종료일은 시작일 이후여야 합니다.", status_code=400)
    status = 200
    try:
        payload = catalogue_data(start, end)
    except CatalogueStorageError as exc:
        status = 503
        payload = {"courses": [], "categories": [{"code": code, "name": name} for code, name in CATEGORIES.items()],
                   "errors": [{"category": "저장소", "message": str(exc)}], "source": "supabase",
                   "fetchedAt": "확인 불가", "start": start.isoformat(), "end": end.isoformat()}
    headers = {"Cache-Control": "no-store"}
    if data:
        return JSONResponse(payload, headers=headers, status_code=status)
    options = "".join(
        f'<option value="{escape(item["code"])}">{escape(item["name"])}</option>'
        for item in payload['categories']
    )
    # Escape '<' so an external course title cannot terminate the JSON script.
    serialized = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")
    rendered = PAGE.replace("__CATEGORY_OPTIONS__", options).replace("__INITIAL_DATA__", serialized)
    try:
        user = get_current_user(request)
    except HTTPException as exc:
        if exc.status_code != 401:
            raise
        user = {"name": "방문자"}
    return HTMLResponse(render_training_page(rendered, user, current="training_posts"),
                        headers=headers, status_code=status)
