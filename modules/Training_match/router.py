"""Authenticated, DB-backed job/profile-to-training recommendations."""
import html
import os
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from modules.auth import auth_store
from modules.Training_match.model import JobRecommendationRequest
from modules.Training_match.page import RECOMMEND_PAGE
from modules.Training_match.repository import get_job, get_own_profile, list_jobs, profile_summary
from modules.Training_match.service import (
    catalogue_data, shortlist_courses, call_groq, validate_recommendations,
    RecommendationError, build_preferences,
)
from modules.training_posts.repository import CatalogueStorageError

router = APIRouter(prefix='/training_match', tags=['교육추천'])


@router.get('', response_class=HTMLResponse)
@router.get('/', response_class=HTMLResponse, include_in_schema=False)
def recommendation_page(request: Request):
    try:
        user, _token = auth_store.authenticated(request)
    except HTTPException as exc:
        if exc.status_code == 401:
            return RedirectResponse('/signin', status_code=303)
        raise
    page = RECOMMEND_PAGE.replace('김나침님', html.escape(user['name'], quote=True) + '님')
    return HTMLResponse(page, headers={'Cache-Control': 'no-store'})


@router.get('/api/context')
def recommendation_context(member: tuple[dict, str] = Depends(auth_store.authenticated)):
    user, token = member
    try:
        jobs = list_jobs()
        profile = get_own_profile(user, token)
        return JSONResponse({'jobs': jobs, 'profile': profile_summary(profile)}, headers={'Cache-Control': 'no-store'})
    except CatalogueStorageError:
        return JSONResponse({'error': '채용공고를 불러오지 못했습니다. 잠시 후 다시 확인해 주세요.'}, status_code=503)


@router.post('/api/recommendations')
def generate_recommendations(body: JobRecommendationRequest,
                             member: tuple[dict, str] = Depends(auth_store.authenticated)):
    user, token = member
    try:
        job = get_job(body.job_id)
        if job is None:
            raise RecommendationError('선택한 채용공고를 찾지 못했습니다. 공고를 다시 선택해 주세요.', 404)
        profile = get_own_profile(user, token)
        summary = profile_summary(profile)
        if not summary['available']:
            raise RecommendationError('마이페이지에 희망 직무·자격증·이수 교육 중 하나 이상 등록한 뒤 추천받아 주세요.', 422)
        if not os.getenv('GROQ_API_KEY', '').strip():
            raise RecommendationError('.env에 GROQ_API_KEY를 설정해 주세요.')
        preferences = build_preferences(job, profile, body)
        today = datetime.now(timezone(timedelta(hours=9))).date()
        payload = catalogue_data(today-timedelta(days=365), today+timedelta(days=365))
        if not payload['courses']:
            raise RecommendationError('저장된 교육이 없습니다. 교육목록 저장 자료를 확인해 주세요.')
        candidates = shortlist_courses(payload, preferences)
        if not candidates:
            raise RecommendationError('교육비·교육 방식에 맞는 교육이 없습니다. 조건을 넓혀서 다시 시도해 주세요.', 422)
        result, model = call_groq(preferences, candidates)
        verified = validate_recommendations(result, candidates)
        return JSONResponse({
            **verified, 'job_title': job['company_name'] + ' · ' + job['title'],
            'job': {'id': job['id'], 'title': job['title'], 'company_name': job['company_name'],
                    'status': job['status'], 'deadline_date': job['deadline_date']},
            'profile_summary': {'target_role': summary['target_role'],
                                'certificate_count': len(summary['certificates']), 'course_count': len(summary['courses'])},
            'preferences': {'budget': body.budget, 'mode': body.mode},
            'meta': {'source': 'groq', 'model': model, 'fetchedAt': payload['fetchedAt'],
                     'fetched_count': len(payload['courses']), 'candidate_count': len(candidates),
                     'failed_categories': len(payload['errors']),
                     'job_source': 'public.job_posting_mj', 'profile_source': 'public.profiles_LYR',
                     'course_source': 'public.training_posts_sms'},
        }, headers={'Cache-Control': 'no-store'})
    except RecommendationError as exc:
        return JSONResponse({'error': exc.message}, status_code=exc.status, headers={'Cache-Control': 'no-store'})
    except CatalogueStorageError:
        return JSONResponse({'error': '저장된 공고·교육 자료를 조회하지 못했습니다. 잠시 후 다시 확인해 주세요.'},
                            status_code=503, headers={'Cache-Control': 'no-store'})
