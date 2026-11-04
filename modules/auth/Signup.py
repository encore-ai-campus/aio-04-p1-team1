""" service로 이동 """

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from modules.auth.auth_ui import render_auth

router = APIRouter(tags=["회원 화면"])


@router.get("/signup", response_class=HTMLResponse, summary="회원가입 페이지")
def signup_page(request: Request):
    return render_auth("signup", getattr(request.app.state, "main_path", None))


def signin_page():
    return render_auth("signin")


app = FastAPI(title="취준나침반 - 회원가입")
app.include_router(router)
app.add_api_route("/signin", signin_page, response_class=HTMLResponse,
                  tags=["회원 화면"], summary="로그인 페이지")


@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse("/signup")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
