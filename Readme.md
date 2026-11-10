# 취준 나침반
 
## Quick Start
```
# 의존성 설치
pip install -r requirements.txt

# 실행(백엔드, 프론트)
uvicorn app:app --reload --env-file .env 
```

## 프로젝트 구조
```text
career-compass/
├── app.py                         # FastAPI 앱 및 기능별 라우터 연결
├── requirements.txt               # Python 의존성
├── docs/                          # 프로젝트 문서
├── modules/                       # 기능 및 데이터 처리 모듈
│   ├── auth/                      # 로그인·회원가입·인증
│   ├── job_posts/                 # 채용 공고 조회
│   ├── jd_match/                  # 채용 공고와 역량 매칭
│   │   └── templates/             # 매칭 화면 템플릿
│   ├── training_posts/            # 교육 공고 조회
│   ├── mypage/                    # 메인·마이페이지·관심 목록
│   ├── main/                      # 메인 화면
│   └── database/                 # 공고 수집 및 DB 저장
│       ├── job_posting/           # 채용 공고 데이터 처리
│       └── training_posting/      # 교육 공고 데이터 처리
├── shared/                        # 공통 설정·DB·UI 컴포넌트
│   ├── config.py                  # 환경 설정
│   ├── database.py                # DB 연결
│   └── components/                # 공통 UI, 스타일, 스크립트, 폰트
├── .env                           # 환경변수 값 (Git 제외)
├── .env.example                   # 팀 공유용 환경변수 예시
├── .gitignore
└── Readme.md
```
