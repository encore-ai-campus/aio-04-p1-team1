"""채용공고 검색 조건과 화면/API 응답 모델."""
from datetime import date
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

SortOrder = Literal['default', 'deadline', 'company']
CareerFilter = Literal['', '신입', '경력', '무관', '신입·경력']

class SearchFilters(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    q: str = Field(default='', max_length=100)
    job: str = Field(default='', max_length=60)
    region: str = Field(default='', max_length=60)
    career: CareerFilter = ''
    employment: str = Field(default='', max_length=40)
    exclude_closed: bool = True
    sort: SortOrder = 'default'
    page: int = Field(default=1, ge=1, le=10000)
    size: int = Field(default=8, ge=1, le=40)

class JobCard(BaseModel):
    id: UUID
    source_url: str
    title: str
    company_name: str
    job_name: str
    region_name: str
    career_type: str | None
    employment_type: str | None
    min_experience_years: int | None
    max_experience_years: int | None
    deadline_type: str | None
    deadline_date: date | None
    use_yn: Literal['Y', 'N']
    is_saved: bool
    is_closed: bool

class JobResults(BaseModel):
    items: list[JobCard]
    total: int
    page: int
    size: int

class FilterOptions(BaseModel):
    jobs: list[str]
    regions: list[str]
    employments: list[str]
