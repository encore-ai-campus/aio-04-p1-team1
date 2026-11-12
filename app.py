from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse
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
