import os
import re
from uuid import UUID

from psycopg import Connection
import requests
from kiwipiepy import Kiwi

from modules.jd_match.model import JobPosting, Profile, SavedJobPosting


def _normalize_company_name(value: str) -> str:
    """기업명 비교를 위해 법인 표기·공백을 정리한다."""
    normalized = re.sub(r"\s+", "", value or "").casefold()
    normalized = re.sub(r"^(주식회사|㈜|\(주\))", "", normalized)
    return normalized


def _extract_skill_candidates(text: str, company_name: str = "") -> list[str]:
    """형태소 품사 기준으로 공고의 명사·기술명 후보를 추출한다."""
    ignored = {"경험", "업무", "가능", "이상", "이하", "이용", "기반", "관련", "대한", "통한"}
    normalized_company_name = _normalize_company_name(company_name)
    result = []
    tokens = Kiwi().tokenize(text or "")
    for index, token in enumerate(tokens):
        if token.tag not in {"NNG", "NNP", "SL", "SH", "SN"}:
            continue
        if index and tokens[index - 1].tag in {"NNG", "NNP"} and tokens[index - 1].start + len(tokens[index - 1].form) == token.start:
            continue
        value = token.form.strip()
        if index + 1 < len(tokens):
            next_token = tokens[index + 1]
            if (
                token.tag in {"NNG", "NNP"}
                and next_token.tag in {"NNG", "NNP"}
                and token.start + len(token.form) == next_token.start
            ):
                value += next_token.form
        # 단일 일반 명사는 시장·과정·변화 같은 일반어가 많이 섞이므로 제외한다.
        # 복합 명사(백+엔드, 데이터+분석)와 고유명사·영문 토큰은 유지한다.
        is_compound_noun = (
            index + 1 < len(tokens)
            and token.tag == "NNG"
            and tokens[index + 1].tag == "NNG"
            and token.start + len(token.form) == tokens[index + 1].start
        )
        if token.tag == "NNG" and not is_compound_noun:
            continue
        if len(value) < 2 or value in ignored or value.lower() in {"the", "and", "for", "with"}:
            continue
        if normalized_company_name and _normalize_company_name(value) == normalized_company_name:
            continue
        if value not in result:
            result.append(value)
    return result[:40]


def get_saved_job_postings(db: Connection, user_id: UUID) -> list[SavedJobPosting]:
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT j.id, j.title, j.company_name
            FROM public.saved_jobs AS s
            JOIN public.job_postings AS j ON j.id = s.job_id
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
            SELECT p.user_id, p.desired_jobs,
                   COALESCE(p.skills, ARRAY[]::text[]) AS skills
            FROM public.profiles AS p
            WHERE p.user_id = %s AND p.use_yn = 'Y'
            """,
            (user_id,),
        )
        row = cursor.fetchone()

    if row is None:
        return None

    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT certification_name AS name, certification_issuer AS organization,
                   certification_acquired_date AS completed_on
            FROM public.profiles_certifications
            WHERE user_id = %s AND use_yn = 'Y'
            ORDER BY certification_name, id
            """,
            (user_id,),
        )
        certificates = cursor.fetchall()
        cursor.execute(
            """
            SELECT training_name AS name, training_provider AS organization,
                   training_completed_date AS completed_on
            FROM public.profiles_trainings
            WHERE user_id = %s AND use_yn = 'Y'
            ORDER BY training_name, id
            """,
            (user_id,),
        )
        courses = cursor.fetchall()

    return Profile(
        user_id=row["user_id"],
        target_role=", ".join(row["desired_jobs"] or [])
        if isinstance(row["desired_jobs"], list)
        else (row["desired_jobs"] or ""),
        certificates=certificates,
        courses=courses,
        skills=[skill.strip() for skill in (row["skills"] or []) if skill and skill.strip()],
    )

# 공고 상세 내용 가져오기
def get_job_posting(db: Connection, job_posting_id: UUID) -> JobPosting | None:
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, source_url, title, company_name,
                   NULL::uuid AS region_id, region_name AS address,
                   employment_type, career_type,
                   min_experience_years * 12 AS min_experience_months,
                   max_experience_years * 12 AS max_experience_months,
                   position_detail, main_tasks,
                   qualifications, preferred_qualifications, deadline_type,
                   deadline_date, use_yn AS status
            FROM public.job_postings
            WHERE id = %s AND use_yn = 'Y'
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
        return {
            "job_id": str(job_posting_id),
            "score_percent": 0,
            "reason": "프로필 또는 공고를 찾을 수 없습니다.",
        }

    api_key = os.getenv("JEV_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("JEV_API_KEY 환경변수를 설정해주세요.")

    candidate_profile = profile.model_dump(mode="json", exclude={"user_id"})
    required_text = "\n".join(
        value for value in (
            job_posting.title,
            job_posting.position_detail,
            job_posting.main_tasks,
            job_posting.qualifications,
            job_posting.preferred_qualifications,
        ) if value
    )
    required_skill_candidates = _extract_skill_candidates(required_text, job_posting.company_name)
    profile_skill_names = profile.skills + [
        item["name"] for item in profile.certificates + profile.courses if item.get("name")
    ]
    normalized_profile_skills = {skill.strip().lower() for skill in profile_skill_names if skill.strip()}
    candidate_missing_skills = [
        skill for skill in required_skill_candidates
        if skill.lower() not in normalized_profile_skills
    ]
    matched_skill_candidates = [
        skill for skill in required_skill_candidates
        if skill.lower() in normalized_profile_skills
    ]
    questions = {
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
                "미입력 정보는 역량 부족으로 단정하지 마세요. "
                "회사명·기업명·브랜드명 자체는 역량으로 세지 마세요. "
                "단, AWS·Excel·Python·ChatGPT·Claude처럼 학습할 수 있는 기술·도구·제품명은 역량으로 유지하세요. "
                "반드시 숫자 점수 하나를 반환하세요."
            ),
            "criteria": [
                "0~19점: 거의 부합하지 않음",
                "20~39점: 일부만 부합함",
                "40~59점: 보통 수준으로 부합함",
                "60~79점: 대부분 부합함",
                "80~100점: 매우 잘 부합함",
            ],
        },
    }
    skill_question_names = {}
    for index, skill in enumerate(candidate_missing_skills):
        name = f"missing_skill_{index}"
        skill_question_names[name] = skill
        questions[name] = {
            "type": "noul",
            "instructions": (
                f"'{skill}'이 이 공고에서 요구되는 역량이고, candidate_profile에 "
                "확인되지 않은 부족 역량인지 판단하세요. 직무 문맥과 별칭을 고려하세요. "
                "회사명·기업명·브랜드명 자체라면 부족 역량으로 판단하지 마세요. "
                "AWS·Excel·Python·ChatGPT·Claude처럼 학습할 수 있는 기술·도구·제품명은 유지하세요."
            ),
        }

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
            "skill_evidence": {
                "required_skill_candidates": required_skill_candidates,
                "candidate_missing_skills": candidate_missing_skills,
            },
        },
        "questions": questions,
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
    response.raise_for_status()

    result = response.json().get("answers", {}).get("qualification_fit", {})
    answers = response.json().get("answers", {})
    missing_skills = [
        skill for name, skill in skill_question_names.items()
        if (answers.get(name) or {}).get("noul", 0) >= 0.5
        and _normalize_company_name(skill) != _normalize_company_name(job_posting.company_name)
    ]
    score = result.get("score")
    probabilities = result.get("probabilities") or {}

    if probabilities:
        expected_score = sum(
            float(str(key).replace("점", "").strip()) * float(value)
            for key, value in probabilities.items()
        )
        if score is None or float(score) <= 4:
            score = expected_score

    # JEV의 score/expected_score(0~4)를 전체 점수의 50% 범위로 환산하고,
    # 기본 점수 50점을 더해 최종 적합도를 계산한다.
    raw_score = max(0, min(float(score or 0), 4))
    score_percent = round(50 + (raw_score * 12.5), 1)
    return {
        "job_id": str(job_posting_id),
        "score_percent": score_percent,
        "jev_score": score,
        "probabilities": probabilities,
        "matched_skills": matched_skill_candidates,
        "missing_skills": missing_skills,
    }
