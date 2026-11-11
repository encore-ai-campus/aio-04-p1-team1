import os
from uuid import UUID

from psycopg import Connection
import requests

from modules.jd_match.model import JobPosting, Profile, SavedJobPosting


def get_saved_job_postings(db: Connection, user_id: UUID) -> list[SavedJobPosting]:
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT j.id, j.title, j.company_name
            FROM public.saved_jobs AS s
            JOIN public.job_posting_mj AS j ON j.id = s.job_id
            WHERE s.user_id = %s AND s.use_yn = 'Y'
            ORDER BY s.created_at DESC NULLS LAST, j.id
            """,
            (user_id,),
        )
        rows = cursor.fetchall()

    return [SavedJobPosting.model_validate(row) for row in rows]

# 프로필 정보(역량) 가져오기
def get_profile(db: Connection, email: str, user_id: UUID) -> Profile | None:
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT p.user_id, p.desired_job, p.certification_name,
                   p.certification_issuer, p.certification_acquired_date,
                   p.training_name, p.training_provider,
                   p.training_completed_date, p.skills
            FROM public.users AS u
            JOIN public.profiles AS p ON p.user_id = u.user_id
            WHERE lower(u.email) = %s AND u.user_id = %s
              AND u.use_yn = 'Y' AND p.use_yn = 'Y'
            """,
            (email.strip().lower(), user_id),
        )
        row = cursor.fetchone()

    if row is None:
        return None

    return Profile(
        user_id=row["user_id"],
        target_role=row["desired_job"] or "",
        certificates=[{
            "name": row["certification_name"],
            "organization": row["certification_issuer"] or "",
            "completed_on": row["certification_acquired_date"],
        }] if row["certification_name"] else [],
        courses=[{
            "name": row["training_name"],
            "organization": row["training_provider"] or "",
            "completed_on": row["training_completed_date"],
        }] if row["training_name"] else [],
        skills=row["skills"] or [],
    )

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
    email: str,
) -> dict:
    profile = get_profile(db, email, user_id)
    job_posting = get_job_posting(db, job_posting_id)

    if profile is None or job_posting is None:
        return {"score_percent": 0, "reason": "프로필 또는 공고를 찾을 수 없습니다."}

    api_key = os.getenv("JEV_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("JEV_API_KEY 환경변수를 설정해주세요.")

    candidate_profile = profile.model_dump(mode="json", exclude={"user_id"})
    payload = {
        "model": "jev-1.13.0",
        "state": {
            "job_requirements": {
                "title": job_posting.title,
                "position_detail": job_posting.position_detail or "",
                "main_tasks": job_posting.main_tasks or "",
                "qualifications": job_posting.qualifications or "",
                "preferred_qualifications": job_posting.preferred_qualifications or "",
            },
            "candidate_profile": candidate_profile,
        },
        "questions": {
            "qualification_fit": {
                "type": "score",
                "instructions": (
                    "공고 제목, 직무 상세, 주요 업무, 자격요건과 우대사항을 "
                    "candidate_profile과 비교하여 적합도를 0점부터 100점까지 평가하세요. "
                    "target_role은 지원자의 희망직무이며 skills는 실제 보유역량입니다. "
                    "희망직무와 공고 직무의 관련성 및 보유역량의 필수요건 충족도를 "
                    "함께 평가하세요. 넓은 희망직무는 하위 직무와의 관련성을 고려하고, "
                    "기술명의 대소문자, 띄어쓰기 및 통용되는 별칭 차이는 동일하게 해석하세요. "
                    "희망직무가 일치한다는 이유만으로 필수역량을 보유했다고 간주하거나, "
                    "저장한 공고를 보유역량으로 간주하지 마세요. "
                    "자격증과 교육은 관련성이 있을 때 보조 근거로 사용하고, "
                    "미입력 정보는 역량 부족으로 단정하지 마세요. "
                    "반드시 숫자 점수 하나를 반환하세요."
                ),
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
