from typing import List

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from psycopg import Connection

from modules.jd_match.model import TestSejo
from modules.jd_match.page import render_match_page
from modules.jd_match.service import get_test_rows
from shared.database import get_db

router = APIRouter(prefix="/jd_match", tags=["jd_match"])


@router.get("", response_class=HTMLResponse)
def match_page():
    return HTMLResponse(render_match_page())


@router.get("/test-db", response_model=List[TestSejo])
def test_db(db: Connection = Depends(get_db)) -> List[TestSejo]:
    return get_test_rows(db)
