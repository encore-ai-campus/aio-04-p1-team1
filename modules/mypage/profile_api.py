"""profiles의 희망 직무·역량 저장·조회 API."""

from contextlib import contextmanager
from datetime import date
from uuid import UUID
import re
import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from psycopg import Connection
from psycopg.errors import ForeignKeyViolation
from pydantic import BaseModel, ConfigDict, Field, field_validator

from shared.auth_dependencies import CurrentUser
from shared.database import get_db
from modules.mypage import profile_entries

router = APIRouter(prefix="/api/mypage", tags=["프로필 정보"])
Database = Annotated[Connection, Depends(get_db)]


class EntryInput(BaseModel):
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


class ProfileItem(EntryInput):
    id: UUID | None = None


class EntryPatch(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str | None = Field(default=None, min_length=1, max_length=100)
    organization: str | None = Field(default=None, max_length=100)
    completed_on: date | None = None

    @field_validator("name")
    @classmethod
    def required_name(cls, value):
        if value is None:
            raise ValueError("이름은 비울 수 없습니다.")
        return value

    @field_validator("completed_on")
    @classmethod
    def past_date(cls, value):
        return EntryInput.past_date(value)


class Profile(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    target_role: str = ""
    certificates: list[ProfileItem] = Field(default_factory=list)
    courses: list[ProfileItem] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    target_role: str = Field(max_length=1000)


def use_member_permissions(cursor, user_id):
    """공통 인증으로 확인한 회원 ID를 현재 트랜잭션의 RLS에 적용합니다."""
    cursor.execute("SET LOCAL ROLE authenticated")
    cursor.execute(
        "SELECT set_config('request.jwt.claims', %s, true), "
        "set_config('request.jwt.claim.sub', %s, true)",
        (json.dumps({"sub": str(user_id), "role": "authenticated"}), str(user_id)),
    )


@contextmanager
def profile_write(db):
    try:
        with db.transaction():
            yield
    except ForeignKeyViolation:
        raise HTTPException(409, "회원 기본정보가 연결되지 않아 저장할 수 없습니다. 회원정보 연결을 확인해 주세요.") from None


def read_profile(cursor, user_id):
    cursor.execute('SELECT desired_jobs FROM public.profiles WHERE user_id=%s', (user_id,))
    row = cursor.fetchone()
    return Profile(
        target_role=", ".join((row["desired_jobs"] or []) if row else []),
        certificates=profile_entries.list_entries(cursor, user_id, "certificates"),
        courses=profile_entries.list_entries(cursor, user_id, "courses"),
    )


@router.get("/profile", response_model=Profile)
def get_profile(user: CurrentUser, db: Database):
    with db.cursor() as cursor:
        use_member_permissions(cursor, user.id)
        return read_profile(cursor, user.id)


@router.put("/profile", response_model=Profile)
def save_profile(body: RoleUpdate, user: CurrentUser, db: Database):
    # 기존 직무 입력 UI를 유지하며 현재 DB의 배열 컬럼에 맞춥니다.
    roles = list(dict.fromkeys(value.strip() for value in body.target_role.split(",") if value.strip()))
    if len(roles) > 20 or any(len(value) > 60 for value in roles):
        raise HTTPException(422, "희망 직무는 각 60자, 최대 20개까지 입력해 주세요.")
    with profile_write(db), db.cursor() as cursor:
        use_member_permissions(cursor, user.id)
        cursor.execute('UPDATE public.profiles SET desired_jobs=%s WHERE user_id=%s RETURNING user_id',
                       (roles, user.id))
        if not cursor.fetchone():
            raise HTTPException(409, "회원 기본 프로필이 없습니다.")
        return read_profile(cursor, user.id)


def register_entry_routes(path, kind):
    @router.get(path, response_model=list[ProfileItem])
    def list_items(user: CurrentUser, db: Database):
        with db.cursor() as cursor:
            use_member_permissions(cursor, user.id)
            return profile_entries.list_entries(cursor, user.id, kind)

    @router.get(path + "/{entry_id}", response_model=ProfileItem)
    def get_item(entry_id: UUID, user: CurrentUser, db: Database):
        with db.cursor() as cursor:
            use_member_permissions(cursor, user.id)
            return profile_entries.get_entry(cursor, user.id, kind, entry_id)

    @router.post(path, response_model=ProfileItem, status_code=201)
    def create_item(body: EntryInput, user: CurrentUser, db: Database):
        with profile_write(db), db.cursor() as cursor:
            use_member_permissions(cursor, user.id)
            return profile_entries.create_entry(cursor, user.id, kind, body)

    @router.patch(path + "/{entry_id}", response_model=ProfileItem)
    def update_item(entry_id: UUID, body: EntryPatch, user: CurrentUser, db: Database):
        with profile_write(db), db.cursor() as cursor:
            use_member_permissions(cursor, user.id)
            return profile_entries.update_entry(cursor, user.id, kind, entry_id, body.model_dump(exclude_unset=True))

    @router.delete(path + "/{entry_id}", status_code=204)
    def delete_item(entry_id: UUID, user: CurrentUser, db: Database):
        with profile_write(db), db.cursor() as cursor:
            use_member_permissions(cursor, user.id)
            profile_entries.delete_entry(cursor, user.id, kind, entry_id)
        return Response(status_code=204)


register_entry_routes("/certifications", "certificates")
register_entry_routes("/trainings", "courses")


class Skills(BaseModel):
    model_config = ConfigDict(extra="forbid")
    skills: list[Annotated[str, Field(min_length=1, max_length=30)]] = Field(default_factory=list, max_length=20)

    @field_validator("skills", mode="before")
    @classmethod
    def clean_skills(cls, values):
        if not isinstance(values, list):
            raise ValueError("역량은 목록으로 입력해 주세요.")
        result, seen = [], set()
        for value in values:
            if not isinstance(value, str) or re.search(r"[\x00-\x1f\x7f]", value):
                raise ValueError("역량은 올바른 문자열로 입력해 주세요.")
            name = re.sub(r"\s+", " ", value.strip().lstrip("#").strip())
            if name.casefold() in seen:
                raise ValueError("이미 추가한 역량입니다.")
            seen.add(name.casefold())
            result.append(name)
        return result


@router.get("/skills", response_model=Skills)
def get_skills(user: CurrentUser, db: Database):
    with db.cursor() as cursor:
        use_member_permissions(cursor, user.id)
        cursor.execute("SELECT skills FROM public.profiles WHERE user_id=%s", (user.id,))
        row = cursor.fetchone()
        return Skills(skills=(row["skills"] or []) if row else [])


@router.put("/skills", response_model=Skills)
def save_skills(body: Skills, user: CurrentUser, db: Database):
    with profile_write(db), db.cursor() as cursor:
        use_member_permissions(cursor, user.id)
        cursor.execute(
            "UPDATE public.profiles SET skills=%s WHERE user_id=%s RETURNING skills",
            (body.skills, user.id),
        )
        row = cursor.fetchone()
        if not row:
            raise HTTPException(409, "회원 기본 프로필이 없습니다.")
        return Skills(skills=row["skills"] or [])
