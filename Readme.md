# 취준 나침반

채용공고와 교육과정을 조회하고 취업 준비를 돕는 FastAPI 프로젝트입니다. 웹 기능은 기능별 모듈에, 테이블 생성·공고 수집·저장 코드는 `modules/database/`에 있습니다.

## 시작하기

```bash
python -m pip install -r requirements.txt
uvicorn app:app --reload --env-file .env
```

`.env.example`을 참고해 프로젝트 루트에 `.env`를 준비합니다. 로그인·회원가입 설정은 [인증 README](modules/auth/README.md)를 확인하세요. 실제 인증키와 DB 연결 문자열은 Git에 올리지 않습니다.

| 환경변수 | 용도 |
|---|---|
| `DATABASE_URL` | PostgreSQL 연결. 웹 DB 조회·저장과 테이블 생성·수집 결과 저장에 사용 |
| `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` | Supabase Auth 연결 |
| `SUPABASE_EMAIL_REDIRECT_URL` | 이메일 인증 후 돌아올 주소 |
| `WORK24_API_KEY` | 고용24 API에서 교육 데이터를 새로 수집할 때 사용 |

서버 실행은 테이블 생성이나 외부 공고 수집을 자동 실행하지 않습니다. 공고 테이블과 프로필·북마크 준비는 아래 명령으로 별도 수행합니다.

## 프로젝트 구조

```text
AIO_project1/
├── app.py                         # FastAPI 앱과 기능별 라우터
├── requirements.txt
├── modules/
│   ├── auth/                      # 로그인·회원가입·회원 정보
│   ├── main/                      # 메인 화면
│   ├── mypage/                    # 프로필·이력·역량·관심 목록
│   ├── job_posts/                 # 채용공고 검색 화면·조회 API
│   ├── training_posts/            # 교육공고 목록 화면·DB 조회
│   ├── jd_match/                  # 채용공고 적합도 분석
│   ├── training_match/            # 교육 추천
│   └── database/
│       ├── README.md
│       ├── table.py               # 프로필 생성 호출·북마크 생성·검증
│       ├── profiles/              # 프로필·자격증·교육 이력, Auth 연동·RLS
│       ├── job_posting/           # 원티드 채용공고 수집·검증·저장
│       └── training_posting/      # 고용24 교육과정 수집·선정·저장
├── shared/                        # 인증 의존성·DB 연결·공통 UI
│   └── components/                # 헤더·사이드바·스타일·스크립트·폰트
├── .env.example
└── Readme.md
```