"""Supabase resumes_LYR API; university fields are not stored."""

from datetime import date
from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field, field_validator
from modules.auth import auth_store

router = APIRouter(prefix="/api/mypage", tags=["이력정보"])

class ResumeItem(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=100)
    organization: str = Field(default="", max_length=100)
    completed_on: date | None = None

    @field_validator("completed_on")
    @classmethod
    def past_date(cls, value):
        if value and value > date.today():
            raise ValueError("취득일·수료일은 오늘 이전으로 입력해 주세요.")
        return value


class Resume(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    target_role: str = Field(default="", max_length=60)
    certificates: list[ResumeItem] = Field(default_factory=list, max_length=50)
    courses: list[ResumeItem] = Field(default_factory=list, max_length=50)


@router.get("/resume", response_model=Resume)
def get_resume(member: tuple[dict, str] = Depends(auth_store.authenticated)):
    user, token = member
    rows = auth_store.supabase_request(
        "GET", "/rest/v1/resumes_LYR", token=token,
        params={"select": "target_role,certificates,courses", "user_id": "eq." + str(user["id"])},
    )
    return Resume.model_validate(rows[0]) if rows else Resume()


@router.put("/resume", response_model=Resume)
def save_resume(body: Resume, member: tuple[dict, str] = Depends(auth_store.authenticated)):
    user, token = member
    rows = auth_store.supabase_request(
        "POST", "/rest/v1/resumes_LYR", token=token,
        params={"on_conflict": "user_id"},
        headers={"Prefer": "resolution=merge-duplicates,return=representation"},
        json={"user_id": str(user["id"]), **body.model_dump(mode="json")},
    )
    if not rows:
        auth_store.failure(503, "이력정보를 저장하지 못했습니다.")
    return Resume.model_validate({key: rows[0][key] for key in Resume.model_fields})


