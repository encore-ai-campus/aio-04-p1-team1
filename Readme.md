# 취준 나침반

채용공고와 교육과정을 조회하고 취업 준비를 돕는 FastAPI 프로젝트입니다. 데이터 수집·DB 테이블 준비 코드는 `modules/database/`에서 관리합니다.

## Quick Start

프로젝트 루트 `AIO_project1`에서 실행합니다.

```bash
python -m pip install -r requirements.txt
uvicorn app:app --reload
```

`.env.example`을 참고해 프로젝트 루트 `.env`에 환경변수를 설정합니다. DB 작업은 `DATABASE_URL`, 고용24 API 조회는 `WORK24_API_KEY`를 사용합니다. 인증용 환경변수는 [인증 README](modules/auth/README.md)를 확인하세요. 실제 키와 연결 문자열은 문서에 기록하지 않습니다.

## 프로젝트 구조

```text
AIO_project1/
├── app.py                          # FastAPI 앱·화면 및 API 라우터 연결
├── modules/
│   ├── auth/                       # 로그인·회원가입 (임이레)
│   ├── database/                   # 데이터 수집·저장·테이블 생성 (이미정)
│   │   ├── README.md
│   │   ├── table.py                # 프로필·북마크 생성 실행 연결
│   │   ├── profiles/               # 프로필·자격증·교육 이력 설계 및 Auth 연동 SQL
│   │   ├── job_posting/            # 원티드 채용공고 검색·수집·저장
│   │   └── training_posting/       # 고용24 교육과정 조회·선정·저장
│   ├── job_posts/                  # 공고 조회 화면·API (이미정)
│   ├── jd_match/                   # 준비 상황 비교 (조상은)
│   ├── training_posts/             # 교육과정 화면·API
│   ├── training_match/             # 교육 추천 (서민석)
│   ├── main/                       # 메인 기능
│   └── mypage/                     # 마이페이지·관심목록·내 정보 (임이레)
├── shared/                         # 공통 설정·DB 연결·UI 구성요소
├── .env                            # 실제 환경변수 (Git 제외)
├── .env.example                    # 공유용 환경변수 예시
├── .gitignore
├── Readme.md
└── requirements.txt
```

## database 구성과 저장 대상

| 위치 | 주요 기능 | DB 테이블 | 상세 설명 |
|---|---|---|---|
| `modules/database/table.py` | 프로필 생성 모듈 호출, 북마크 생성·권한·기존 데이터 보존 검증 | `saved_jobs`, `saved_trainings` 및 프로필 3개 테이블 | [database README](modules/database/README.md) |
| `modules/database/profiles/` | 최종 프로필 구조 생성, Auth 초기 반영·가입 트리거·저장 RPC·RLS | `public.profiles`, `public.profiles_certifications`, `public.profiles_trainings` | [프로필 README](modules/database/profiles/README.md) |
| `modules/database/job_posting/` | 원티드 직무별 검색, 전체/샘플 수집, 저장 없는 확인 | `public.job_postings` | [채용공고 README](modules/database/job_posting/README.md) |
| `modules/database/training_posting/` | 고용24 API 조회, 직무별 교육 선정, 저장·검증 | `public.training_posting` | [교육과정 README](modules/database/training_posting/README.md) |

### 프로필 설계

`profiles.user_id`는 `auth.users.id`를 직접 참조합니다. 별도 `public.users`를 전제로 하지 않으며, 생성 코드에서 기존 사용자 테이블을 이전하거나 삭제하지 않습니다.

- 이름·이메일은 필수이고, `desired_jobs`와 `skills`는 NULL을 허용하는 `text[]` 배열입니다.
- 자격증과 교육 이수 기록은 각각 여러 행으로 저장하며 프로필을 참조합니다.
- 이름 수정 권한, 본인 접근 제한, 활성 여부를 반영한 접근 정책을 정의합니다.
- 기존 Auth 회원 중 프로필이 없는 회원만 초기 반영하고 기존 프로필·이력을 덮어쓰지 않습니다.
- `profiles_trainings`는 사용자가 입력하는 수료 이력으로, 고용24 교육공고인 `training_posting`과 다릅니다.

**현재 웹 연동 상태:** `auth`와 `mypage` 변경은 원복되어 이름 조회·수정은 `auth_LYR`, 프로필 조회·저장은 `profiles_LYR`를 사용합니다. `database`에 준비한 새 프로필 구조·RPC와 화면/API를 연결하는 작업은 별도 연동 범위입니다.

### 채용공고·교육과정 수집

두 수집 기능 모두 개발자·데이터 분석가·인사·총무·회계·생산관리·마케팅·기획자 직무를 기준으로 합니다.

채용공고는 `source.txt`에 직무별 링크를 저장하고 `collect.py`에서 전체·샘플·확인 모드를 실행합니다. HTML은 메모리에서 처리하며, 결과는 CSV와 TXT 보고서로 확인합니다. 신입 공고의 최대 경력은 NULL, 마감 날짜는 `date`로 저장합니다. 생성 SQL은 최종 구조의 `job_postings.sql` 하나로 관리합니다.

교육과정은 고용24의 국민내일배움카드 훈련과정 목록 API를 사용합니다. 직무별 관련성과 중복을 확인해 최대 125개씩 선정하며 JSON·XML·검증 보고서를 사용합니다. 외부 과정 ID는 `work24_training_id`, 내부 UUID는 `id`입니다. 북마크의 `saved_trainings.training_id`는 이 내부 UUID를 참조합니다.

## DB 작업 실행 예시

프로필 생성 SQL 확인과 롤백 검증:

```bash
python -m modules.database.profiles.table --print-sql
python -m modules.database.profiles.table --dry-run
```

프로필·북마크를 함께 준비하는 작업의 롤백 검증:

```bash
python -m modules.database.table --dry-run
```

위 생성 명령에서 `--dry-run`을 제거하면 실제 반영합니다. 상위 `table.py`는 공고 테이블 자체를 생성하지 않으며, 기존 북마크가 참조하는 공고 테이블을 우선합니다. 새 공고 테이블과 기존 북마크의 연결 관계는 [database README](modules/database/README.md)를 확인하세요.

원티드 기존 목록에서 미저장 공고 전체 수집·저장:

```bash
python -m modules.database.job_posting.collect --all --save
```

원티드 실제 공고 3건 확인만 수행 (결과 파일·DB 저장 없음):

```bash
python -m modules.database.job_posting.collect --check
```

고용24 응답 필드 설명 확인과 기존 교육 JSON의 DB 저장:

```bash
python -m modules.database.training_posting.work24_client --list-fields
python -m modules.database.training_posting.save_to_supabase
```

검색어·직무 분류 기준, 신규 수집 옵션, 파일별 역할과 테스트 명령은 각 폴더의 README를 확인하세요. 수집을 다시 실행하면 결과 파일이 해당 실행 범위로 갱신될 수 있습니다.
