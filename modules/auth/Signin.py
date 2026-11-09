"""로그인 페이지: python -m uvicorn Signin:app --reload --port 8002"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from modules.auth.auth_store import create_app
from modules.auth.auth_ui import render_auth

router = APIRouter(tags=["회원 화면"])


@router.get("/signin", response_class=HTMLResponse, summary="로그인 페이지")
def signin_page(request: Request):
    return render_auth("signin", getattr(request.app.state, "main_path", None))


def signup_page():
    return render_auth("signup")


app = create_app("취준나침반 - 로그인")
app.include_router(router)
app.add_api_route("/signup", signup_page, response_class=HTMLResponse,
                  tags=["회원 화면"], summary="회원가입 페이지")


@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse("/signin")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
