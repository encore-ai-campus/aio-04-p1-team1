"""Validate selected-job lookup and the analyzed skills sent for AI recommendations."""
from typing import Annotated, Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class JobRecommendationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    job_id: UUID


class RecommendationInput(BaseModel):
    job_title: str = Field(min_length=1, max_length=300)
    job_text: str = Field(min_length=10, max_length=5000)
    skills: str = Field(default="", max_length=12000)
    goals: str = Field(default="", max_length=300)
    budget: int | None = Field(default=None, ge=0, le=10000000)
    mode: Literal["all", "online_first", "online_only"] = "all"
    missing_skills: list[str] = Field(default_factory=list)


class MissingSkillsRecommendationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    missing_skills: list[Annotated[str, Field(min_length=1, max_length=200)]] = Field(
        min_length=1, max_length=200
    )
