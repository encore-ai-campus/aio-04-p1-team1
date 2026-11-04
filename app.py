from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from modules.auth.Signin import router as signin_router
from modules.auth.Signup import router as signup_router
from modules.job_posts.router import router as job_postsrouter
from modules.jd_match.router import router as jd_matchrouter
from modules.training_match.router import router as training_matchrouter
from modules.mypage.Mypage import router as mypagerouter

app = FastAPI(title="Career Compass")
app.state.main_path = "/main"

app.include_router(signin_router)
app.include_router(signup_router)
app.include_router(job_postsrouter)
app.include_router(jd_matchrouter)
app.include_router(training_matchrouter)
app.include_router(mypagerouter)


@app.get("/")
def root():
    return RedirectResponse("/signin")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
