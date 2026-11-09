"""통합 실행: python -m uvicorn yire.app:app --env-file yire/.env --reload --port 8000.

/main의 임시 화면을 팀원 메인 화면 라우터로 교체하세요.
Streamlit 챗봇은 Chatbot.py를 별도 실행하거나 render_chatbot을 import합니다.
"""

from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse

from modules.auth import auth_store
from modules.mypage import bookmarks_api
from modules.mypage import resume_api
from modules.auth.Signup import router as signup_router
from modules.auth.Signin import router as signin_router
from modules.mypage.Mypage import router as mypage_router
from modules.mypage.Mypage import render_member_page, page_user


app = auth_store.create_app("취준나침반 - 회원·마이페이지")
app.description = "회원가입 → 로그인 → 메인 → 마이페이지. 관심 목록 API는 로그인한 회원의 데이터만 처리합니다."
app.state.main_path = "/main"
app.include_router(signup_router)
app.include_router(signin_router)
app.include_router(mypage_router)
app.include_router(bookmarks_api.router)
app.include_router(resume_api.router)


@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse("/signin")


@app.get("/main", response_class=HTMLResponse, tags=["연결 확인"], summary="팀원 메인 화면 연결 전 임시 화면")
def main_page(request: Request):
    user = page_user(request)
    if isinstance(user, RedirectResponse):
        return user
    return render_member_page("main", user)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("yire.app:app", host="127.0.0.1", port=8000, env_file="yire/.env")
