"""로그인 회원의 공고 검색 화면과 조회 API. 북마크는 기존 /api/bookmarks 사용."""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from psycopg import Connection, Error
from shared.auth_dependencies import CurrentUser
from shared.database import get_db
from modules.auth import auth_store
from .search_models import SearchFilters, JobResults, FilterOptions
from .job_repository import search_jobs, get_filter_options
from .search_page import render_job_search

router = APIRouter(prefix='/job_posts',tags=['채용공고'])
Database = Annotated[Connection, Depends(get_db)]

@router.get('',response_class=HTMLResponse,summary='채용공고 검색 화면')
def jobs_page(request: Request):
    try:
        user, _ = auth_store.authenticated(request)
    except HTTPException as exc:
        if exc.status_code == 401:
            return RedirectResponse('/signin',status_code=303)
        raise
    return HTMLResponse(render_job_search(user))

@router.get('/api/filters',response_model=FilterOptions,summary='실제 공고 기준 필터 선택지')
def filter_options(user: CurrentUser, db: Database):
    try:
        return get_filter_options(db)
    except Error:
        raise HTTPException(503,'검색 조건을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.') from None

@router.get('/api/jobs',response_model=JobResults,summary='공고 검색·페이지별 저장 여부 조회')
def jobs(user: CurrentUser, db: Database, filters: Annotated[SearchFilters, Depends()]):
    try:
        return search_jobs(db,user.id,filters)
    except Error:
        raise HTTPException(503,'공고를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.') from None
