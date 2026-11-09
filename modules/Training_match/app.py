"""호환용 진입점. 통합 실행은 프로젝트 루트 app.py를 사용하세요."""
from fastapi import FastAPI
from modules.Training_match.router import router

app = FastAPI()
app.include_router(router)
