"""로그인한 사용자의 플랫폼 알림 설정 조회 및 저장."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection
from pydantic import BaseModel, ConfigDict, Field

from shared.auth_dependencies import CurrentUser
from shared.database import get_db

router = APIRouter(tags=["채용공고 모니터링"])
Database = Annotated[Connection, Depends(get_db)]


class PlatformSetting(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    id: UUID | None = None
    platform_name: str = Field(min_length=1, max_length=200)
    platform_email: str = Field(min_length=3, max_length=320, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    user_email: str = Field(min_length=3, max_length=320, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class SettingsSave(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: list[PlatformSetting] = Field(max_length=100)


def read_settings(db, user_id):
    return db.execute(
        "SELECT id, platform_name, platform_email, user_email "
        "FROM public.platform_settings WHERE user_id = %s AND use_yn = 'Y' "
        "ORDER BY created_at, id", (user_id,),
    ).fetchall()


@router.get("/api/job-monitoring/settings")
def get_settings(user: CurrentUser, db: Database):
    return {"items": read_settings(db, user.id)}


@router.put("/api/job-monitoring/settings")
def save_settings(body: SettingsSave, user: CurrentUser, db: Database):
    with db.transaction():
        # 사용자별 저장을 직렬화하여 한 번의 저장을 원자적으로 반영합니다.
        db.execute("SELECT user_id FROM public.profiles WHERE user_id = %s FOR UPDATE", (user.id,))
        existing = {row["id"] for row in read_settings(db, user.id)}
        ids = [item.id for item in body.items if item.id is not None]
        if len(ids) != len(set(ids)) or not set(ids).issubset(existing):
            raise HTTPException(400, "저장 목록이 변경되었습니다. 새로고침 후 다시 시도해주세요.")
        for setting_id in existing - set(ids):
            db.execute(
                "UPDATE public.platform_settings SET use_yn = 'N' WHERE id = %s AND user_id = %s",
                (setting_id, user.id),
            )
        for item in body.items:
            values = (item.platform_name, item.platform_email, item.user_email)
            if item.id:
                db.execute(
                    "UPDATE public.platform_settings SET platform_name = %s, platform_email = %s, "
                    "user_email = %s WHERE id = %s AND user_id = %s",
                    (*values, item.id, user.id),
                )
            else:
                db.execute(
                    "INSERT INTO public.platform_settings (platform_name, platform_email, user_email, user_id) "
                    "VALUES (%s, %s, %s, %s)", (*values, user.id),
                )
        items = read_settings(db, user.id)
    return {"items": items}
