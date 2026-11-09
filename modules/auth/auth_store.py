"""Supabase Auth + auth_LYR 프로필 API 및 회원 JWT 기반 REST 요청."""

from contextlib import asynccontextmanager
import os
import re
from urllib.parse import urlparse

import httpx

from fastapi import APIRouter, FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from shared.auth_dependencies import User

LEGACY_COOKIE_NAME = "compass_supabase_session"
ACCESS_COOKIE_NAME = "compass_supabase_access"
REFRESH_COOKIE_NAME = "compass_supabase_refresh"
SESSION_SECONDS = 60 * 60 * 24
api = APIRouter(prefix="/api/auth", tags=["회원 인증"])
SIGNUP_MESSAGE = "입력하신 이메일로 인증 메일을 확인해 주세요. 이메일 인증 후 로그인할 수 있습니다. 이미 가입한 경우 기존 계정으로 로그인해 주세요."


def configuration():
    url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    key = os.environ.get("SUPABASE_PUBLISHABLE_KEY", "").strip()
    redirect = os.environ.get("SUPABASE_EMAIL_REDIRECT_URL", "").strip()
    if not url.startswith("https://") or not key or not redirect:
        raise RuntimeError("SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, SUPABASE_EMAIL_REDIRECT_URL 환경변수를 설정해 주세요. yire/README.md 참고")
    parsed = urlparse(redirect)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.fragment:
        raise RuntimeError("이메일 인증 복귀 URL을 확인해 주세요.")
    return url, key, redirect


@asynccontextmanager
async def lifespan(app):
    configuration()
    yield


def apply_auth_cookies(request, response):
    # 인증 함수는 API와 HTML 화면 양쪽에서 호출됩니다. 최종 응답에 갱신 쿠키를 반영합니다.
    secure = request.url.scheme == "https" or configuration()[2].startswith("https://")
    if getattr(request.state, "clear_auth_cookies", False):
        for name in (ACCESS_COOKIE_NAME, REFRESH_COOKIE_NAME, LEGACY_COOKIE_NAME):
            response.delete_cookie(name, path="/", secure=secure, httponly=True, samesite="lax")
    elif session := getattr(request.state, "auth_cookie_update", None):
        for name, key in ((ACCESS_COOKIE_NAME, "access_token"), (REFRESH_COOKIE_NAME, "refresh_token")):
            response.set_cookie(name, session[key], max_age=SESSION_SECONDS, httponly=True,
                                secure=secure, samesite="lax", path="/")
        response.delete_cookie(LEGACY_COOKIE_NAME, path="/")


def verified_session(request):
    """쿠키를 신뢰하지 않고 Supabase Auth에서 사용자와 토큰을 검증합니다."""
    if cached := getattr(request.state, "verified_auth", None):
        return cached
    access_token = request.cookies.get(ACCESS_COOKIE_NAME)
    refresh_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if access_token:
        try:
            user = supabase_request("GET", "/auth/v1/user", token=access_token)
            request.state.verified_auth = (user, access_token)
            return user, access_token
        except HTTPException as exc:
            if exc.status_code != 401:
                raise  # 장애나 요청 제한을 토큰 만료로 간주하지 않습니다.
    if not refresh_token:
        request.state.clear_auth_cookies = True
        failure(401, "로그인이 필요하거나 만료되었습니다. 다시 로그인해 주세요.")
    try:
        session = supabase_request("POST", "/auth/v1/token", params={"grant_type": "refresh_token"},
                                   json={"refresh_token": refresh_token})
        user = supabase_request("GET", "/auth/v1/user", token=session["access_token"])
    except HTTPException as exc:
        if exc.status_code in {401, 403}:
            request.state.clear_auth_cookies = True
        raise
    request.state.auth_cookie_update = session
    request.state.verified_auth = (user, session["access_token"])
    return user, session["access_token"]


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
            if path == "/rest/v1/bookmarks_LYR" and code == "23505":
                raise HTTPException(status_code=409, detail={
                    "code": "BOOKMARK_ALREADY_EXISTS", "message": "이미 저장한 정보입니다.",
                })
            if result.status_code == 401:
                failure(401, "로그인이 만료되었습니다. 다시 로그인해 주세요.")
            failure(503, "데이터를 처리하지 못했습니다. Supabase 테이블과 접근 권한 설정을 확인해 주세요.")
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


@api.post("/signup", status_code=202, summary="회원가입 및 인증 메일 요청")
def signup(body: SignupRequest):
    supabase_request("POST", "/auth/v1/signup",
                     params={"redirect_to": configuration()[2]},
                     json={"email": body.email, "password": body.password, "data": {"name": body.name}})
    return {"email_confirmation_required": True, "message": SIGNUP_MESSAGE}



@api.post("/signin", response_model=User, summary="로그인 (Supabase Auth 쿠키 발급)")
def signin(body: SigninRequest, request: Request):
    session = supabase_request("POST", "/auth/v1/token", params={"grant_type": "password"},
                               json={"email": body.email, "password": body.password})
    user = supabase_request("GET", "/auth/v1/user", token=session["access_token"])
    result = profile(user, session["access_token"])
    request.state.auth_cookie_update = session
    return result


def authenticated(request: Request):
    user, access_token = verified_session(request)
    return profile(user, access_token), access_token


@api.get("/me", response_model=User, summary="현재 로그인한 회원")
def me(request: Request):
    return authenticated(request)[0]


@api.post("/signout", status_code=204, summary="로그아웃")
def signout(request: Request, response: Response):
    try:
        if request.cookies.get(ACCESS_COOKIE_NAME) or request.cookies.get(REFRESH_COOKIE_NAME):
            try:
                _, token = verified_session(request)
            except HTTPException as exc:
                if exc.status_code not in {401, 403}:
                    raise
            else:
                supabase_request("POST", "/auth/v1/logout", token=token, params={"scope": "local"})
    finally:
        request.state.clear_auth_cookies = True
    response.status_code = 204
    return response


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    name: str = Field(min_length=2, max_length=30, description="표시 이름")


@api.patch("/me", response_model=User, summary="내 표시 이름 수정")
def update_profile(body: ProfileUpdate, request: Request):
    user, access_token = authenticated(request)
    rows = supabase_request("PATCH", "/rest/v1/auth_LYR", token=access_token,
                            params={"id": "eq." + user["id"], "select": "id,name"},
                            headers={"Prefer": "return=representation"}, json={"name": body.name})
    if not rows or rows[0]["id"] != user["id"]:
        failure(503, "이름을 수정하지 못했습니다. 접근 권한을 확인해 주세요.")
    return {**user, "name": rows[0]["name"]}


def create_app(title):
    app = FastAPI(title=title, version="1.1.0", lifespan=lifespan,
                  description="회원가입 → 이메일 인증 → 로그인 → 현재 회원 확인 → 로그아웃")
    app.include_router(api)

    @app.get("/auth/confirmed", response_class=HTMLResponse, include_in_schema=False)
    def email_confirmed():
        # 인증 처리는 Supabase가 수행합니다. URL 토큰을 앱 서버나 로그로 보내지 않습니다.
        return HTMLResponse("""<!doctype html><html lang="ko"><meta charset="utf-8"><title>이메일 인증</title>
        <p>인증 결과를 확인하고 로그인 화면으로 이동합니다.</p>
        <script>const error=new URLSearchParams(location.hash.slice(1)).has('error')||new URLSearchParams(location.search).has('error');
        history.replaceState(null,'','/auth/confirmed');location.replace(error?'/signin?confirmation_error=1':'/signin?confirmed=1');</script>
        <noscript>이메일 인증 결과를 확인한 후 <a href="/signin">로그인</a>해 주세요.</noscript></html>""",
        headers={"Referrer-Policy": "no-referrer"})

    @app.middleware("http")
    async def browser_origin_check(request: Request, call_next):
        origin = request.headers.get("origin")
        if request.method in {"POST", "PUT", "PATCH", "DELETE"} and origin and origin != str(request.base_url).rstrip("/"):
            return JSONResponse(status_code=403, content={"detail": "다른 사이트에서 보낸 요청은 허용하지 않습니다."})
        response = await call_next(request)
        apply_auth_cookies(request, response)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        errors = [{"field": str(error["loc"][-1]), "message": error["msg"].removeprefix("Value error, ")} for error in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": errors[0]["message"], "errors": errors})

    return app
