"""요청한 job_postings 17개 컬럼에 대응하는 수집 모델."""
from dataclasses import dataclass

@dataclass(frozen=True)
class JobPosting:
    source_url: str
    title: str
    company_name: str
    job_name: str
    region_name: str
    employment_type: str | None
    career_type: str | None
    min_experience_years: int | None
    max_experience_years: int | None
    position_detail: str | None
    main_tasks: str | None
    qualifications: str | None
    preferred_qualifications: str | None
    deadline_type: str | None
    deadline_date: str | None  # YYYY-MM-DD, DB 타입 date
    use_yn: str
    id: str | None = None  # 최초 INSERT 시 DB의 gen_random_uuid()로 채웁니다.
