# 취준 나침반

채용공고와 교육과정을 조회하고 취업 준비를 돕는 FastAPI 프로젝트입니다. 데이터 수집·DB 테이블 준비 코드는 `modules/database/`에서 관리합니다.

## Quick Start

# 실행(백엔드, 프론트)
uvicorn app:app --reload --env-file .env 
```

`.env.example`을 참고해 프로젝트 루트 `.env`에 환경변수를 설정합니다. DB 작업은 `DATABASE_URL`, 고용24 API 조회는 `WORK24_API_KEY`를 사용합니다. 인증용 환경변수는 [인증 README](modules/auth/README.md)를 확인하세요. 실제 키와 연결 문자열은 문서에 기록하지 않습니다.

## 프로젝트 구조

```text
career-compass/
├── app.py                         # FastAPI 앱 및 기능별 라우터 연결
├── requirements.txt               # Python 의존성
├── docs/                          # 프로젝트 문서(산출물)
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
