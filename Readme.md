# 취준 나침반
 
## Quick Start
```
# 의존성 설치
pip install -r requirements.txt

# api 실행
uvicorn main:app --reload

# streamlit 실행 
streamlit run app.py
```

## 프로젝트 구조
```text
career-compass/
├── main.py                 # FastAPI 실행 · 전체 모듈 API 연결
├── app.py                  # Streamlit 실행 · 전체 모듈 화면 연결
├── config.py               # 공통 설정 · 환경변수
├── database.py             # DB 연결
├── modules/                # 기능별 작업 폴더
│   ├── job_posts/              # 공고 조회(이미정)
│   │   ├── page.py                 # Streamlit 화면
│   │   ├── router.py               # API 요청 · 응답
│   │   ├── service.py              # 처리 로직 · DB 및 외부 API 호출
│   │   └── model.py                # DB 테이블 모델
│   ├── jd_match/               # 준비 상황 비교 (조상은)
│   ├── training_match/         # 교육 추천 (서민석)
│   └── mypage/                 # 내 정보 (로그인) (김이레)
├── .env                    # API 키 등 환경변수 값 (Git 제외)
├── .env.example            # 팀 공유용 환경변수 예시
├── .gitignore              # Git에서 제외할 파일 목록
└── requirements.txt        # 필요한 패키지 목록
```