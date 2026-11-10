"""job_postings 테이블에 맞춘 원티드 수집 결과."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class WantedJobPost:
    id: str
    source_url: str
    title: str
    company_name: str
    region_id: Optional[str]
    address: Optional[str]
    employment_type: Optional[str]
    career_type: str
    min_experience_months: Optional[int]
    max_experience_months: Optional[int]
    position_detail: Optional[str]
    main_tasks: Optional[str]
    qualifications: Optional[str]
    preferred_qualifications: Optional[str]
    deadline_type: str
    deadline_date: Optional[str]
    status: str
