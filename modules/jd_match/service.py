import os
from uuid import UUID

from psycopg import Connection
import requests

from modules.jd_match.model import JobPosting, Profile

# 프로필 정보(역량) 가져오기
def get_profile(db: Connection, user_id: UUID) -> Profile | None:
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT user_id, target_role, certificates, courses
            FROM "profiles_LYR"
            WHERE user_id = %s
            """,
            (user_id,),
        )
        row = cursor.fetchone()

    return Profile.model_validate(row) if row else None

# 공고 상세 내용 가져오기
# job_post_id = '0183a987-1cdf-5048-a9e8-d5eedce2e177'
def get_job_posting(db: Connection, job_posting_id: UUID) -> JobPosting | None:
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, source_url, title, company_name, region_id, address,
                   employment_type, career_type, min_experience_months,
                   max_experience_months, position_detail, main_tasks,
                   qualifications, preferred_qualifications, deadline_type,
                   deadline_date, status
            FROM job_posting_mj
            WHERE id = %s
            """,
            (job_posting_id,),
        )
        row = cursor.fetchone()

    return JobPosting.model_validate(row) if row else None

# 적합도 계산
def get_jd_match_score(
    db: Connection,
    user_id: UUID,
    job_posting_id: UUID,
) -> dict:
    profile = get_profile(db, user_id)
    job_posting = get_job_posting(db, job_posting_id)

    if profile is None or job_posting is None:
        return {"score_percent": 0, "reason": "프로필 또는 공고를 찾을 수 없습니다."}

    api_key = os.getenv("JEV_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("JEV_API_KEY 환경변수를 설정해주세요.")

    payload = {
        "model": "jev-1.13.0",
        "state": {
            "job_requirements": {
                "qualifications": job_posting.qualifications or "",
                "preferred_qualifications": job_posting.preferred_qualifications or "",
            },
            "candidate_profile": {
                "target_role": profile.target_role,
                "certificates": profile.certificates,
                "courses": profile.courses,
            },
        },
        "questions": {
            "qualification_fit": {
                "type": "score",
                "instructions": "공고의 자격요건과 우대사항 대비 지원자의 적합도를 0점부터 100점까지 백분율 점수로 평가하세요. 반드시 숫자 점수 하나를 반환하세요.",
                "criteria": [
                    "0~19점: 거의 부합하지 않음",
                    "20~39점: 일부만 부합함",
                    "40~59점: 보통 수준으로 부합함",
                    "60~79점: 대부분 부합함",
                    "80~100점: 매우 잘 부합함",
                ],
            }
        },
    }

    response = requests.post(
        "https://api.typesafe.ai/v1/systemone",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )
    print(f"[JEV] response status={response.status_code} body={response.text[:2000]}", flush=True)
    response.raise_for_status()

    result = response.json().get("answers", {}).get("qualification_fit", {})
    score = result.get("score")
    probabilities = result.get("probabilities") or {}

    if probabilities:
        expected_score = sum(
            float(str(key).replace("점", "").strip()) * float(value)
            for key, value in probabilities.items()
        )
        print(
            f"[JEV] parsed score={score} probabilities={probabilities} "
            f"expected_score={expected_score}",
            flush=True,
        )
        if score is None or float(score) <= 4:
            score = expected_score

    score_percent = round(max(0, min(float(score or 0), 100)), 1)
    print(f"[JEV] score_percent={score_percent}", flush=True)
    return {
        "score_percent": score_percent,
        "jev_score": score,
        "probabilities": probabilities,
    }
