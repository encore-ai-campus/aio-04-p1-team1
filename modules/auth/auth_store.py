"""Supabase Auth + auth_LYR 프로필 API. 외부 설정은 수동 승인 후 적용합니다."""

import os
import re
import time
from urllib.parse import urlparse
from uuid import UUID

import httpx

from fastapi import HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

COOKIE_NAME = "compass_supabase_session"
SIGNUP_MESSAGE = "입력하신 이메일로 인증 메일을 확인해 주세요. 이메일 인증 후 로그인할 수 있습니다. 이미 가입한 경우 기존 계정으로 로그인해 주세요."


def configuration():
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")
    redirect = os.environ.get("SUPABASE_EMAIL_REDIRECT_URL", "")
    if not url.startswith("https://") or not key or not redirect:
        raise RuntimeError("SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, SUPABASE_EMAIL_REDIRECT_URL 환경변수를 설정해 주세요. INTEGRATION.md 참고")
    parsed = urlparse(redirect)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.fragment:
        raise RuntimeError("이메일 인증 복귀 URL을 확인해 주세요.")
    return url, key, redirect


class User(BaseModel):
    id: UUID
    name: str
    email: str


class SignupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=2, max_length=30, examples=["나침반"])
    email: str = Field(max_length=254, examples=["compass@example.com"])
    password: str = Field(min_length=8, max_length=128, repr=False, examples=["Demo12345"])
    password_confirm: str = Field(min_length=8, max_length=128, repr=False, examples=["Demo12345"])

    @field_validator("name")
    @classmethod
    def clean_name(cls, value):
        value = value.strip()
        if len(value) < 2:
            raise ValueError("이름은 공백을 제외하고 2자 이상 입력해 주세요.")
        return value

    @field_validator("email")
    @classmethod
    def clean_email(cls, value):
        return normalize_email(value)

    @field_validator("password")
    @classmethod
    def check_password(cls, value):
        if not re.search(r"[A-Za-z]", value) or not re.search(r"[0-9]", value):
            raise ValueError("비밀번호는 영문과 숫자를 모두 포함해 주세요.")
        return value

    @model_validator(mode="after")
    def check_confirmation(self):
        if self.password != self.password_confirm:
            raise ValueError("비밀번호 확인이 일치하지 않습니다.")
        return self


def normalize_email(value):
    value = value.strip().lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
        raise ValueError("올바른 이메일 주소를 입력해 주세요.")
    return value


class SigninRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(max_length=254, examples=["compass@example.com"])
    password: str = Field(min_length=1, max_length=128, repr=False, examples=["Demo12345"])

    @field_validator("email")
    @classmethod
    def clean_email(cls, value):
        return normalize_email(value)



def failure(status_code, message):
    raise HTTPException(status_code=status_code, detail=message)


def supabase_request(method, path, *, token=None, json=None, params=None, headers=None):
    url, key, _ = configuration()
    request_headers = {"apikey": key, **(headers or {})}
    if token:
        request_headers["Authorization"] = f"Bearer {token}"
    try:
        with httpx.Client(timeout=10) as client:
            result = client.request(method, url + path, headers=request_headers, json=json, params=params)
    except httpx.RequestError:
        failure(503, "인증 서버에 연결하지 못했습니다. 잠시 후 다시 시도해 주세요.")
    if result.is_error:
        try:
            code = result.json().get("error_code", result.json().get("code", ""))
        except (ValueError, AttributeError):
            code = ""
        if result.status_code == 429:
            failure(429, "요청이 많습니다. 잠시 후 다시 시도해 주세요.")
        if code == "email_not_confirmed":
            failure(403, "이메일 인증 후 로그인해 주세요. 받은 메일함을 확인해 주세요.")
        if code in {"user_already_exists", "email_exists"} and path == "/auth/v1/signup":
            return {}  # 기존 계정 존재 여부를 노출하지 않는 동일 안내
        if path.startswith("/rest/"):
            failure(503, "회원정보를 처리하지 못했습니다. 테이블과 접근 권한 설정을 확인해 주세요.")
        if result.status_code in {400, 401, 403, 422}:
            if path == "/auth/v1/signup":
                failure(400, "가입 정보를 확인해 주세요. 가입이 제한된 경우 관리자에게 문의해 주세요.")
            failure(401, "이메일 또는 비밀번호를 확인하거나 다시 로그인해 주세요.")
        failure(503, "인증 서버에서 요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.")
    if not result.content:
        return None
    try:
        return result.json()
    except ValueError:
        failure(503, "인증 서버 응답을 확인하지 못했습니다.")


def profile(user, access_token):
    if not user.get("email_confirmed_at"):
        failure(403, "이메일 인증 후 로그인해 주세요.")
    rows = supabase_request("GET", "/rest/v1/auth_LYR", token=access_token,
                            params={"select": "id,name", "id": "eq." + user["id"]})
    if not rows or rows[0]["id"] != user["id"]:
        failure(503, "회원정보가 없습니다. auth_LYR 테이블과 가입 트리거 설정을 확인해 주세요.")
    return {"id": user["id"], "name": rows[0]["name"], "email": user["email"]}


def signup(body: SignupRequest):
    supabase_request("POST", "/auth/v1/signup",
                     params={"redirect_to": configuration()[2]},
                     json={"email": body.email, "password": body.password, "data": {"name": body.name}})
    return {"email_confirmation_required": True, "message": SIGNUP_MESSAGE}



def signin(body: SigninRequest, request: Request, response: Response):
    session = supabase_request("POST", "/auth/v1/token", params={"grant_type": "password"},
                               json={"email": body.email, "password": body.password})
    # 사용자 정보는 인증 서버에서 재확인하고 프로필은 해당 JWT의 RLS로 조회합니다.
    user = supabase_request("GET", "/auth/v1/user", token=session["access_token"])
    result = profile(user, session["access_token"])
    response.set_cookie(COOKIE_NAME, session["access_token"], max_age=int(session["expires_in"]), httponly=True,
                        secure=request.url.scheme == "https", samesite="lax", path="/")
    response.set_cookie(COOKIE_NAME + "_refresh", session["refresh_token"],
                        max_age=60 * 60 * 24 * 30, httponly=True,
                        secure=request.url.scheme == "https", samesite="lax", path="/")
    return result


def authenticated(request):
    access_token = request.cookies.get(COOKIE_NAME)
    refresh_token = request.cookies.get(COOKIE_NAME + "_refresh")
    if not access_token and not refresh_token:
        failure(401, "로그인이 필요합니다.")
    if not access_token:
        failure(401, "로그인이 만료되었습니다. 다시 로그인해 주세요.")
    try:
        user = supabase_request("GET", "/auth/v1/user", token=access_token)
    except HTTPException as exc:
        if exc.status_code != 401 or not refresh_token:
            raise
        session = supabase_request("POST", "/auth/v1/token", params={"grant_type": "refresh_token"},
                                   json={"refresh_token": refresh_token})
        access_token = session["access_token"]
        user = supabase_request("GET", "/auth/v1/user", token=access_token)
    if not user.get("id"):
        failure(401, "다시 로그인해 주세요.")
    return profile(user, access_token), access_token


def me(request: Request):
    return authenticated(request)[0]


def signout(request: Request, response: Response):
    access_token = request.cookies.get(COOKIE_NAME)
    response.delete_cookie(COOKIE_NAME, path="/")
    response.delete_cookie(COOKIE_NAME + "_refresh", path="/")
    if access_token:
        try:
            supabase_request("POST", "/auth/v1/logout", token=access_token, params={"scope": "local"})
        except HTTPException:
            pass
    response.status_code = 204
    return response


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=2, max_length=30, description="표시 이름")


def update_profile(body: ProfileUpdate, request: Request):
    user, access_token = authenticated(request)
    rows = supabase_request("PATCH", "/rest/v1/auth_LYR", token=access_token,
                            params={"id": "eq." + user["id"], "select": "id,name"},
                            headers={"Prefer": "return=representation"}, json={"name": body.name})
    if not rows or rows[0]["id"] != user["id"]:
        failure(503, "이름을 수정하지 못했습니다. 접근 권한을 확인해 주세요.")
    return {**user, "name": rows[0]["name"]}


