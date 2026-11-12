"""로그인 회원용 챗봇 API. 별도의 페이지나 앱을 만들지 않습니다."""

from typing import Literal
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from shared.auth_dependencies import CurrentUser
from .service import ChatbotError, reply


router = APIRouter(prefix="/api/chatbot", tags=["챗봇"])


@router.get("/assets/{filename}", include_in_schema=False)
def mascot_asset(filename: Literal["nachimi.png", "nachimi-poses.png", "nachimi-question.png"]):
    return FileResponse(Path(__file__).with_name("assets") / filename,
                        media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})


class ChatTurn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=1800)


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    message: str = Field(min_length=1, max_length=500)
    history: list[ChatTurn] = Field(default_factory=list, max_length=12)


@router.post("/messages")
async def chat(body: ChatRequest, user: CurrentUser):
    headers = {"Cache-Control": "no-store"}
    try:
        result = await reply(body.message, [turn.model_dump() for turn in body.history])
    except ChatbotError as exc:
        return JSONResponse({"detail": str(exc)}, status_code=exc.status, headers=headers)
    return JSONResponse(result, headers=headers)
