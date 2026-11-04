from fastapi import FastAPI
from modules.job_posts.router import router as job_postsrouter
from modules.jd_match.router import router as jd_matchrouter
from modules.training_match.router import router as training_matchrouter
from modules.mypage.router import router as mypagerouter

app = FastAPI(title="Career Compass")

app.include_router(job_postsrouter)
app.include_router(jd_matchrouter)
app.include_router(training_matchrouter)
app.include_router(mypagerouter)


@app.get("/")
def root():
    return {"message": "Career Compass API 실행 중"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
