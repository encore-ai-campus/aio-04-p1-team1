"""Supabase bookmarks_LYR API. Run the integrated app:app server."""

from datetime import datetime
from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path as ApiPath, Query, Response
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from modules.auth import auth_store

class ItemType(str, Enum):
    job = "job"
    course = "course"


class BookmarkCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "item_type": "job",
                    "source": "saramin",
                    "source_id": "demo-job-001",
                    "title": "[샘플] HR팀 신입 채용",
                    "organization": "샘플 기업",
                    "original_url": "https://example.com/jobs/demo-job-001",
                    "location": "서울 서초구",
                    "deadline": None,
                },
                {
                    "item_type": "course",
                    "source": "manual",
                    "source_id": "demo-course-001",
                    "title": "[샘플] 인사 데이터 분석 교육",
                    "organization": "샘플 교육기관",
                    "original_url": "https://example.com/courses/demo-course-001",
                    "cost": 0,
                    "is_online": True,
                },
            ]
        },
    )

    item_type: ItemType = Field(description="job: 채용공고 / course: 교육과정")
    source: str = Field(min_length=1, max_length=100, description="제공처 식별자. 예: saramin, manual")
    source_id: str = Field(min_length=1, max_length=200, description="제공처 내 원본 ID. 직접 등록 시 고유 ID 사용")
    title: str = Field(min_length=1, max_length=300, description="공고 또는 교육 제목")
    organization: str = Field(min_length=1, max_length=200, description="회사 또는 교육기관명")
    original_url: HttpUrl = Field(description="원문 주소. http 또는 https")
    location: str | None = Field(default=None, max_length=200, description="지역. 알 수 없으면 null")
    deadline: datetime | None = Field(default=None, description="마감 시각. 불명 또는 채용 시 마감은 null. 입력 시 시간대 포함 권장")
    cost: int | None = Field(default=None, ge=0, description="교육비(원). 무료는 0, 알 수 없으면 null")
    is_online: bool | None = Field(default=None, description="온라인 여부. 알 수 없으면 null")


class Bookmark(BookmarkCreate):
    id: int
    user_id: str
    created_at: datetime


class BookmarkCounts(BaseModel):
    all: int
    job: int
    course: int


class BookmarkList(BaseModel):
    items: list[Bookmark]
    total: int = Field(description="현재 필터·검색 조건에 맞는 전체 개수")
    counts: BookmarkCounts = Field(description="필터·검색과 무관한 사용자 전체 저장 개수. 탭 표시용")
    page: int
    size: int


Member = Annotated[tuple[dict, str], Depends(auth_store.authenticated)]
BookmarkId = Annotated[int, ApiPath(ge=1)]
router = APIRouter(tags=["관심 정보"])
TABLE = "/rest/v1/bookmarks_LYR"


def not_found():
    raise HTTPException(status_code=404, detail={
        "code": "BOOKMARK_NOT_FOUND", "message": "저장한 정보를 찾을 수 없습니다.",
    })


@router.post("/api/bookmarks", response_model=Bookmark, status_code=201, summary="공고·교육 저장")
def create_bookmark(body: BookmarkCreate, member: Member):
    user, token = member
    rows = auth_store.supabase_request(
        "POST", TABLE, token=token,
        headers={"Prefer": "return=representation"},
        json={**body.model_dump(mode="json"), "user_id": str(user["id"])},
    )
    if not rows:
        auth_store.failure(503, "관심목록을 저장하지 못했습니다.")
    return rows[0]


@router.get("/api/bookmarks", response_model=BookmarkList, summary="저장 목록 조회·필터·검색")
def list_bookmarks(
    member: Member,
    item_type: Annotated[ItemType | None, Query()] = None,
    q: Annotated[str | None, Query(max_length=100)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    _, token = member
    return auth_store.supabase_request(
        "POST", "/rest/v1/rpc/list_bookmarks_lyr", token=token,
        json={"p_item_type": item_type.value if item_type else None,
              "p_query": q.strip() if q else None, "p_page": page, "p_size": size},
    )


@router.get("/api/bookmarks/{bookmark_id}", response_model=Bookmark, summary="저장 정보 상세 조회")
def read_bookmark(bookmark_id: BookmarkId, member: Member):
    user, token = member
    rows = auth_store.supabase_request(
        "GET", TABLE, token=token,
        params={"select": "*", "id": f"eq.{bookmark_id}", "user_id": "eq." + str(user["id"])},
    )
    if not rows:
        not_found()
    return rows[0]


@router.delete("/api/bookmarks/{bookmark_id}", status_code=204, summary="저장 취소")
def delete_bookmark(bookmark_id: BookmarkId, member: Member):
    user, token = member
    rows = auth_store.supabase_request(
        "DELETE", TABLE, token=token, headers={"Prefer": "return=representation"},
        params={"id": f"eq.{bookmark_id}", "user_id": "eq." + str(user["id"])},
    )
    if not rows:
        not_found()
    return Response(status_code=204)


# Standalone use also requires authentication; no demo user_id=1 fallback.
app = auth_store.create_app("취준나침반 - Supabase 관심목록 API")
app.include_router(router)


