from typing import Optional
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from typing import Any

# 내 프로필
class Profile(BaseModel):
    user_id: UUID
    target_role: str
    certificates: list[dict[str, Any]]
    courses: list[dict[str, Any]]

# 공고
class JobPosting(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_url: str
    title: str
    company_name: str

    region_id: UUID | None = None
    address: str | None = None
    employment_type: str | None = None
    career_type: str

    min_experience_months: int | None = None
    max_experience_months: int | None = None

    position_detail: str | None = None
    main_tasks: str | None = None
    qualifications: str | None = None
    preferred_qualifications: str | None = None

    deadline_type: str
    deadline_date: date | None = None
    status: str
