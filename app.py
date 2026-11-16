from pathlib import Path

from fastapi import HTTPException, Request
from fastapi.middleware.gzip import GZipMiddleware
from shared.components.static_assets import ASSETS, asset_url
from fastapi.responses import FileResponse, RedirectResponse
from modules.auth.Signin import router as signin_router
from modules.auth.Signup import router as signup_router
from modules.auth import auth_store
from modules.job_posts.router import router as job_posts_router
from modules.jd_match.router import router as jd_match_router
from modules.training_posts.router import router as training_posts_router
from modules.training_match.router import router as training_match_router
from modules.mypage.router import router as mypage_router
from modules.main.router import router as main_router
from modules.chatbot.router import router as chatbot_router

# 로그인, 회원가입 후 이동할 주소
app = auth_store.create_app("취준나침반 - 회원·마이페이지")
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)
app.description = "회원가입 → 로그인 → 메인 → 마이페이지. 관심 목록 API는 로그인한 회원의 데이터만 처리합니다."
app.state.main_path = "/main"

app.include_router(signin_router)
app.include_router(signup_router)
app.include_router(job_posts_router)
app.include_router(jd_match_router)
app.include_router(training_posts_router)
app.include_router(training_match_router)
app.include_router(mypage_router)
app.include_router(main_router)
app.include_router(chatbot_router)

@app.get("/assets/compass/{version}/{name}", include_in_schema=False)
def public_asset(version: str, name: str):
    if name not in ASSETS or asset_url(name) != f"/assets/compass/{version}/{name}":
        raise HTTPException(404, "파일을 찾을 수 없습니다.")
    media_type = "font/woff2" if name.endswith(".woff2") else "image/png"
    return FileResponse(ASSETS[name], media_type=media_type,
                        headers={"Cache-Control": "public, max-age=31536000, immutable"})


GOOGLE_VERIFY_FILE = "googleca9d4096df3c76fc.html"


@app.get(f"/{GOOGLE_VERIFY_FILE}", include_in_schema=False)
def google_verification_file():
    return FileResponse(Path(__file__).with_name(GOOGLE_VERIFY_FILE))

@app.get("/")
def root(request: Request):
    try:
        auth_store.verified_session(request)
    except HTTPException as exc:
        if exc.status_code == 401:
            return RedirectResponse("/signin", status_code=303)
        raise
    return RedirectResponse("/main", status_code=303)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
