from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from modules.auth.Signin import router as signin_router
from modules.auth.Signup import router as signup_router
from modules.auth.router import callback_router as auth_callback_router
from modules.auth.router import router as auth_router
from modules.job_posts.router import router as job_posts_router
from modules.jd_match.router import router as jd_match_router
from modules.training_posts.router import router as training_posts_router
from modules.mypage.router import router as mypage_router
from modules.auth import auth_store

app = FastAPI(title="Career Compass")

# 로그인, 회원가입 후 이동할 주소
app.state.main_path = "/main"
app = auth_store.create_app("취준나침반 - 회원·마이페이지")
app.description = "회원가입 → 로그인 → 메인 → 마이페이지. 관심 목록 API는 로그인한 회원의 데이터만 처리합니다."

app.include_router(signin_router)
app.include_router(signup_router)
app.include_router(auth_router)
app.include_router(auth_callback_router)
app.include_router(job_posts_router)
app.include_router(jd_match_router)
app.include_router(training_posts_router)
app.include_router(mypage_router)


@app.middleware("http")
async def browser_origin_check(request, call_next):
    origin = request.headers.get("origin")
    if request.method in {"POST", "PUT", "PATCH", "DELETE"} and origin and origin != str(request.base_url).rstrip("/"):
        return JSONResponse(status_code=403, content={"detail": "다른 사이트에서 보낸 요청은 허용하지 않습니다."})
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    errors = [{"field": str(error["loc"][-1]), "message": error["msg"].removeprefix("Value error, ")} for error in exc.errors()]
    return JSONResponse(status_code=422, content={"detail": errors[0]["message"], "errors": errors})


@app.get("/")
def root():
    return RedirectResponse("/signin")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
