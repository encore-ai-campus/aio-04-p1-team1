# 취준 나침반
 
## Quick Start
```
# 의존성 설치
pip install -r requirements.txt

# 실행(백엔드, 프론트)
# uvicorn app:app --reload
uvicorn app:app --reload --env-file .env 
```

## 프로젝트 구조
```text
career-compass/
├── app.py                      # FastAPI 앱 · 화면 및 API 라우터 연결
├── modules/                    # 기능별 작업 폴더
│   ├── auth/                   # 로그인 · 회원가입(임이레)
│   │   ├── 기존 소스
│   ├── job_posts/              # 공고 조회 (이미정)
│   │   ├── ...    
│   ├── jd_match/               # 준비 상황 비교 (조상은)
│   │   ├── page.py                 # 화면용 파일
│   │   ├── router.py               # API 라우터
│   │   ├── service.py              # 처리 로직용 파일
│   │   └── model.py                # 모델용 파일
│   ├── training_match/         # 교육 추천 (서민석)
│   │   ├── ...
│   └── mypage/                 # 임시 홈 · 마이페이지 · 관심목록 · 내 정보 (임이레)
│       ├── 기존소스
├── shared/                     # 함께 사용하는 코드
│   ├── config.py                   # 공통 설정용 파일
│   ├── database.py                 # DB 연결용 파일
│   └── components/                 # 공통 UI(기존소스)
│       ├── header.py
│       └── menu.py
├── .env                            # 환경변수 값 (Git 제외)
├── .env.example                    # 팀 공유용 환경변수 예시
├── .gitignore
├── Readme.md
└── requirements.txt
```
'''


## 교육 기능 통합 (복사본)
이 폴더는 C:\career-compass 원본을 유지하고 만든 통합 작업 복사본입니다.
가상환경·캐시·Git 이력을 제외한 소스와 .env를 복사했습니다.
training_posts와 training_match는 별도 모듈이며, 기존 FastAPI 앱에 각각 라우터로 연결했습니다.

### 실행
```powershell
cd C:\career-compass-integrated
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000
```
- 로그인: http://127.0.0.1:8000/signin
- 교육목록: http://127.0.0.1:8000/training_posts
- 교육추천: http://127.0.0.1:8000/training_match
- 추천 API: POST /training_match/api/recommendations
- 목록 JSON: GET /training_posts?data=1

### 수정 범위
- 루트 app.py: 루트 .env 로드와 교육추천 라우터 등록
- 두 교육 모듈: router(경로), page(화면), service(API 처리), model(입력 검증) 구조로 변경
- 교육목록·교육추천 모듈은 router.py로 연결하며, 서버 진입점은 루트 app.py 하나만 사용
- 목록 재조회·추천 요청 URL을 통합 경로로 변경
- 기존 회원 메인 화면에 교육목록/추천 진입 링크 추가
- 기존 로그인·회원가입·마이페이지 및 적합도 라우터 유지

### 데이터와 설정
실제 API 키는 기존 .env에 유지하며 shared에 값을 추가하지 않았습니다.
각 교육 모듈 .env에서 WORK24_API_KEY를 읽고, 추천 모듈은 GROQ_API_KEY/GROQ_MODEL도 읽습니다.
새 라이브러리를 추가하거나 제거하지 않았으므로 루트 requirements.txt는 기존 항목을 유지합니다.
교육모음 데이터는 public.training_posts_sms에 저장합니다. 공고 입력과 AI 추천 결과는 DB에 저장하지 않습니다.
교육 화면 하트는 기존처럼 브라우저 저장이며 회원 관심목록 DB와 자동 동기화하지 않습니다.
추천은 선택한 DB 채용공고와 로그인 회원 프로필을 비교하며, 기존 적합도 점수와는 별도로 교육을 추천합니다.
공고모음 라우터는 원본에서 비어 있어 공고 화면을 새로 구현하지 않았습니다.

### 기존 실행 차단 문제 수정
적합도 라우터에서 사용하지 않는 DB import 두 개를 제거했습니다. 기존 DB 테스트는 이미 주석 처리되어 있습니다.
Windows에서 psycopg DLL이 차단되더라도 DB를 사용하지 않는 화면·교육 API를 실행할 수 있습니다.
shared/database.py와 DB 의존성은 유지했습니다. 실제 PostgreSQL 연결 기능은 이번 검증 범위에 포함하지 않습니다.

### 통합 검증 결과 (2026-11-09)
- 통합 앱 시작 및 로그인 화면·기존 로그인 이동 동작 확인
- 교육목록 HTML/JSON, 재조회 URL, 날짜 역전 오류 처리 확인
- 추천 화면, 입력 검증(422), 외부 API 오류 안내, 다른 사이트 요청 차단 확인
- 화면 JavaScript 문법 및 API 키 HTML 미노출 확인
- 실제 고용24 24개 분류에서 480개 조회, 실패 분류 0개
- 실제 Groq openai/gpt-oss-20b 추천 요청 HTTP 200, 실제 후보 교육 3개와 추천 이유 확인
- 원본 소스 및 설정 48개 파일의 해시 일치 확인
- Edge 화면 자동 검증 및 실제 회원 로그인/DB 쓰기는 수행하지 않음


## 교육목록 Supabase 저장 방식 (2026-11-09 변경)
교육모음은 public.training_posts_sms에 저장된 자료만 읽습니다.
대분류 24개별 최신 훈련 시작일순 최대 20개, 총 최대 480개를 저장합니다.
동일 기관·과정·회차는 중복 저장하지 않으며 같은 교육은 기존 ID를 유지해 갱신합니다.
API 조회가 일부 실패하거나 DB 저장·건수 검증에 실패하면 전체 저장을 취소하고 기존 자료를 유지합니다.
자동 갱신, 서버 시작 시 수집, 예약 작업, 화면 업데이트 버튼은 없습니다.
검색/조건 적용/초기화는 DB 재조회이며 고용24 API를 호출하지 않습니다.
필요할 때만 프로젝트 루트에서 명시적으로 다음 명령을 실행할 수 있습니다.
```powershell
.\.venv\Scripts\python.exe -m modules.training_posts.import_training_posts
```
조회 범위는 실행일 기준 전후 365일이며, 최신 기준은 등록일이 아닌 교육 시작일입니다.
분야별 실제 조회 결과가 20개 미만이면 존재하는 자료만 저장합니다.
DB 접속은 shared.database.get_db()의 공통 DB 세션과 루트 .env의 DATABASE_URL을 사용합니다.
공통 세션에서 SSL 연결과 트랜잭션을 관리하며 별도 인증서 파일은 사용하지 않습니다.
교육추천도 저장된 교육을 후보로 사용하며 Groq로 공고와 본인 프로필을 비교합니다.

### DB 저장 검증 결과
- public.training_posts_sms: 24개 분류 각각 20개, 총 480개 저장
- 기관·과정·회차 기준 중복 0건
- 교육 HTML 및 JSON 응답에서 저장 자료 480개 확인
- 고용24 API 호출을 차단한 상태에서도 화면·조건 재조회 정상 동작
- 앱 시작 및 화면 재조회 전후 건수와 최종 저장 시각 동일: 자동 갱신 없음
- 기존 회원/교육추천 통합 검사와 JavaScript 문법 검사 통과


## 채용공고·내 프로필 매칭 (2026-11-09)
- 로그인한 회원이 교육추천 화면에서 채용공고를 선택하고 추천받기를 누릅니다.
- public.job_posting_mj: 공고 ID로 업무·자격요건·우대사항 조회
- public.profiles_LYR: 로그인 회원의 user_id와 Supabase JWT/RLS로 본인 프로필만 조회
- public.training_posts_sms: 저장된 교육 480개에서 조건에 맞는 후보 선정
- Groq가 공고 요구 역량과 자격증·이수 교육을 비교하여 최대 3개 교육과 짧은 추천 이유를 반환
- 희망 직무는 보유 능력으로 간주하지 않고, 이수 교육만으로 숙련도나 경력을 단정하지 않습니다.
- 프로필 항목이 모두 비어 있으면 마이페이지 등록을 안내합니다.
- 공고와 프로필을 직접 입력하는 방식 및 가상 예시 버튼을 제거했습니다.
- 이름·이메일·회원 ID는 Groq에 보내지 않습니다. 추천 버튼을 누를 때 필요한 학습/공고 정보만 전송합니다.
- 공고·프로필 원본과 교육 저장 자료를 수정하거나 자동 갱신하지 않습니다.
- 공고 마감 여부는 선택창 안내에서 확인하세요. 공고 상태만으로 현재 지원 가능 여부를 보장하지 않습니다.

### 연결 경로
- GET /training_match : 로그인한 회원의 추천 화면 (미로그인 시 /signin)
- GET /training_match/api/context : 공고 목록과 본인 프로필 요약
- POST /training_match/api/recommendations : {job_id, goals?, budget?, mode?}
- /training_match?job_id=<공고 UUID> 로 이동하면 해당 공고를 선택합니다.
- 클라이언트가 보내는 user_id, 임의 공고 내용, 타인 프로필은 허용하지 않습니다.
- 라이브러리 추가/제거 없음. 기존 requirements.txt 유지.

### 프로필 매칭 검증 결과
- 실제 job_posting_mj 공고 35개 조회 및 profiles_LYR 프로필 2개 구조 확인
- 실제 DB 공고 + 검증용 가상 프로필 + 저장 교육 480개로 Groq 호출 성공, 교육 2개 추천
- 검증 과정에서 실제 회원 프로필은 Groq에 전송하지 않음
- JWT와 본인 user_id 필터 적용, 미로그인 요청 차단, 타인 user_id/임의 skills 요청 거부 검사 통과
- 없는 공고/빈 프로필/DB 오류 안내, JavaScript 문법 및 기존 통합 검사 통과
- 실제 회원 로그인 세션으로 끝까지 진행하는 화면 검증은 수행하지 않음
- 검사 실행: `.\.venv\Scripts\python.exe tests\verify_integration.py`
