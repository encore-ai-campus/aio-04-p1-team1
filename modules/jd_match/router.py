from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from psycopg import Connection

# from modules.jd_match.model import TestSejo
# from modules.jd_match.service import get_test_rows
from shared.components.header import render_header
from shared.database import get_db

router = APIRouter(prefix="/jd_match", tags=["jd_match"])
TEMPLATE_PATH = Path(__file__).with_name("templates") / "match.html"


def render_match_page():
    page = TEMPLATE_PATH.read_text(encoding="utf-8")
    return page.replace("__HEADER__", render_header(member=True))


@router.get("", response_class=HTMLResponse)
def match_page():
    return HTMLResponse(render_match_page())


# @router.get("/test-db", response_model=List[TestSejo])
# def test_db(db: Connection = Depends(get_db)) -> List[TestSejo]:
#     return get_test_rows(db)

from shared.auth_dependencies import CurrentUser

@router.get("/my-data")
def get_my_data(user: CurrentUser):
    return {"user_id": str(user.id)}
