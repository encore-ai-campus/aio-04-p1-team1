"""AI 추천 요청 검증 모델. DB 저장용 모델이 아닙니다."""
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class RecommendationInput(BaseModel):
    job_title: str = Field(min_length=1, max_length=300)
    job_text: str = Field(min_length=10, max_length=5000)
    skills: str = Field(default="", max_length=12000)
    goals: str = Field(default="", max_length=300)
    budget: int | None = Field(default=None, ge=0, le=10000000)
    mode: Literal["all", "online_first", "online_only"] = "all"


class JobRecommendationRequest(BaseModel):
    """User identity and profile contents cannot be supplied by the client."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    job_id: UUID
    goals: str = Field(default="", max_length=300)
    budget: int | None = Field(default=None, ge=0, le=10000000)
    mode: Literal["all", "online_first", "online_only"] = "all"
