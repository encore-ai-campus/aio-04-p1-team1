"""Authenticated, role-based course lookup from the stored catalogue."""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from shared.auth_dependencies import get_current_user
from modules.training_posts.page import render_training_page
from modules.training_posts.repository import CatalogueStorageError
from modules.training_match.model import JobRecommendationRequest, MissingSkillsRecommendationRequest, RecommendationInput
from modules.training_match.page import RECOMMEND_PAGE
from modules.training_match.repository import get_job, list_jobs
from modules.training_match.service import (
    catalogue_data, courses_for_job, shortlist_courses, call_gemini,
    validate_recommendations, RecommendationError,
)

router = APIRouter(prefix="/training_match", tags=["교육추천"])


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def recommendation_page(request: Request):
    try:
        user = get_current_user(request)
    except HTTPException as exc:
        if exc.status_code == 401:
            return RedirectResponse("/signin", status_code=303)
        raise
    page = render_training_page(RECOMMEND_PAGE, user, current="training_match")
    return HTMLResponse(page, headers={"Cache-Control": "no-store"})


@router.get("/api/context")
def recommendation_context(user=Depends(get_current_user)):
    try:
        return JSONResponse({"jobs": list_jobs()}, headers={"Cache-Control": "no-store"})
    except CatalogueStorageError:
        return JSONResponse({"error": "채용공고를 불러오지 못했습니다. 잠시 후 다시 확인해 주세요."},
                            status_code=503, headers={"Cache-Control": "no-store"})


@router.post("/api/recommendations")
def generate_recommendations(body: JobRecommendationRequest, user=Depends(get_current_user)):
    try:
        job = get_job(body.job_id)
        if job is None:
            return JSONResponse({"error": "선택한 채용공고를 찾지 못했습니다. 공고를 다시 선택해 주세요."},
                                status_code=404, headers={"Cache-Control": "no-store"})
        today = datetime.now(timezone(timedelta(hours=9))).date()
        payload = catalogue_data(today-timedelta(days=365), today+timedelta(days=365))
        roles, items = courses_for_job(payload, job)
        return JSONResponse({"job": job, "roles": roles, "items": items,
            "meta": {"source": "job_role", "fetchedAt": payload["fetchedAt"],
                     "fetched_count": len(payload["courses"]), "limit": 15}},
            headers={"Cache-Control": "no-store"})
    except CatalogueStorageError:
        return JSONResponse({"error": "공고 또는 교육 자료를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요."},
                            status_code=503, headers={"Cache-Control": "no-store"})


@router.post('/api/skill-recommendations')
def recommend_missing_skills(body: MissingSkillsRecommendationRequest,
                             user=Depends(get_current_user)):
    """Use the tab's analyzed gaps without looking up an unrelated job/profile table."""
    skills = list(dict.fromkeys(body.missing_skills))
    preferences = RecommendationInput(
        job_title='적합도 분석에서 확인한 부족 역량 보완',
        job_text='적합도 분석 결과의 부족 역량을 보완하는 교육과정을 찾습니다.',
        missing_skills=skills,
    )
    try:
        today = datetime.now(timezone(timedelta(hours=9))).date()
        payload = catalogue_data(today-timedelta(days=365), today+timedelta(days=365))
        candidates = shortlist_courses(payload, preferences)
        result, model = call_gemini(preferences, candidates)
        if not isinstance(result, dict):
            raise RecommendationError('AI 분석 결과가 올바르지 않습니다. 다시 추천받아 주세요.')
        excluded = result.get('excluded_company_names', [])
        if not isinstance(excluded, list) or any(not isinstance(name, str) or name not in skills for name in excluded):
            raise RecommendationError('회사명 분류 결과를 확인하지 못했습니다. 다시 추천받아 주세요.')
        excluded = list(dict.fromkeys(excluded))
        skills = [skill for skill in skills if skill not in excluded]
        verified = validate_recommendations(result, candidates)
        if not skills:
            verified = {'analysis': {'summary': '회사명을 제외한 보완 역량이 없습니다.', 'gaps': []},
                        'items': [], 'certificates': []}
        return JSONResponse({
            **verified, 'missing_skills': skills, 'excluded_company_names': excluded, 'job_title': '부족 역량 맞춤 교육',
            'meta': {'source': 'gemini', 'model': model, 'fetchedAt': payload['fetchedAt'],
                     'fetched_count': len(payload['courses']), 'candidate_count': len(candidates),
                     'failed_categories': len(payload['errors'])},
        }, headers={'Cache-Control': 'no-store'})
    except RecommendationError as exc:
        return JSONResponse({'error': exc.message}, status_code=exc.status, headers={'Cache-Control': 'no-store'})
    except CatalogueStorageError:
        return JSONResponse({'error': '교육 자료를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.'},
                            status_code=503, headers={'Cache-Control': 'no-store'})
