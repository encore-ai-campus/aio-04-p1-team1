"""공통 인증·DB 연결을 사용하는 saved_jobs / saved_trainings 관심목록 API."""

from datetime import datetime
from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path as ApiPath, Query, Response
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from psycopg import Connection
from shared.auth_dependencies import CurrentUser
from shared.database import get_db
from modules.mypage import bookmarks_store

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
                    "source_id": "00000000-0000-0000-0000-000000000001",
                    "title": "[샘플] HR팀 신입 채용",
                    "organization": "샘플 기업",
                    "original_url": "https://example.com/jobs/demo-job-001",
                    "location": "서울 서초구",
                    "deadline": None,
                },
                {
                    "item_type": "course",
                    "source": "manual",
                    "source_id": "00000000-0000-0000-0000-000000000002",
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
    source: str = Field(default="", max_length=100, description="제공처 식별자. 예: saramin, manual")
    source_id: str = Field(min_length=1, max_length=200, description="원본 공고 테이블의 UUID. 교육 외부 ID·원문 URL은 유일하게 식별되는 경우에만 지원")
    title: str = Field(default="", max_length=300, description="공고 또는 교육 제목")
    organization: str = Field(default="", max_length=200, description="회사 또는 교육기관명")
    original_url: HttpUrl | None = Field(default=None, description="원문 주소. http 또는 https")
    location: str | None = Field(default=None, max_length=200, description="지역. 알 수 없으면 null")
    deadline: datetime | None = Field(default=None, description="마감 시각. 불명 또는 채용 시 마감은 null. 입력 시 시간대 포함 권장")
    cost: int | None = Field(default=None, ge=0, description="교육비(원). 무료는 0, 알 수 없으면 null")
    is_online: bool | None = Field(default=None, description="온라인 여부. 알 수 없으면 null")


class Bookmark(BookmarkCreate):
    id: str
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


Database = Annotated[Connection, Depends(get_db)]
BookmarkId = Annotated[str, ApiPath(pattern=r"^(job|course):[0-9a-fA-F-]{36}$")]
router = APIRouter(tags=["관심 정보"])


@router.post("/api/bookmarks", response_model=Bookmark, status_code=201, summary="공고·교육 저장")
def create_bookmark(body: BookmarkCreate, user: CurrentUser, db: Database):
    return bookmarks_store.create_item(db, user.id, body)


@router.get("/api/bookmarks", response_model=BookmarkList, summary="저장 목록 조회·필터·검색")
def list_bookmarks(
    user: CurrentUser,
    db: Database,
    item_type: Annotated[ItemType | None, Query()] = None,
    q: Annotated[str | None, Query(max_length=100)] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return bookmarks_store.list_items(db, user.id, item_type.value if item_type else None, q, page, size)


@router.get("/api/bookmarks/{bookmark_id}", response_model=Bookmark, summary="저장 정보 상세 조회")
def read_bookmark(bookmark_id: BookmarkId, user: CurrentUser, db: Database):
    return bookmarks_store.read_item(db, user.id, bookmark_id)


@router.delete("/api/bookmarks/{bookmark_id}", status_code=204, summary="저장 취소")
def delete_bookmark(bookmark_id: BookmarkId, user: CurrentUser, db: Database):
    bookmarks_store.delete_item(db, user.id, bookmark_id)
    return Response(status_code=204)
