# database — 테이블 생성과 데이터 수집

`modules/database/`는 프로필·북마크 테이블 준비와 원티드 채용공고·고용24 교육과정 수집을 담당합니다. 모든 명령은 프로젝트 루트 `AIO_project1`에서 실행합니다.

| 경로 | 역할 | 상세 문서 |
|---|---|---|
| [table.py](table.py) | 프로필 모듈 호출, 북마크 생성·권한 설정·데이터 보존 검증 | 아래 설명 |
| [profiles/](profiles/) | 최종 프로필·자격증·교육 이력 생성, Auth 연동, 권한·RPC | [profiles/README.md](profiles/README.md) |
| [job_posting/](job_posting/) | 원티드 검색·수집·검증, `public.job_postings` 저장 | [job_posting/README.md](job_posting/README.md) |
| [training_posting/](training_posting/) | 고용24 교육 수집·선정·검증, `public.training_posting` 저장 | [training_posting/README.md](training_posting/README.md) |

## 현재 파일 구성

```text
modules/database/
├── README.md
├── table.py
├── profiles/
│   ├── README.md
│   ├── __init__.py
│   ├── table.py
│   ├── profile_functions.sql
│   ├── profile_checks.py
│   └── test_profiles_api.py
├── job_posting/
│   ├── README.md
│   ├── collect.py
│   ├── wanted_crawler.py
│   ├── schemas.py
│   ├── save_to_supabase.py
│   ├── job_postings.sql
│   ├── test_wanted_crawler.py
│   ├── source.txt
│   └── results/
└── training_posting/
    ├── README.md
    ├── collect.py
    ├── work24_client.py
    ├── schemas.py
    ├── save_to_supabase.py
    ├── training_posting.sql
    ├── test_work24_api.py
    ├── test_collection.py
    └── results/
```

채용 수집은 `job_posting/collect.py` 하나에서 전체·샘플·저장 없는 확인 모드를 실행합니다. 별도 수집·확인 파일과 마이그레이션 SQL은 통합되어 없습니다. 교육 수집 코드는 고용24의 조회·선정 흐름에 따라 분리되어 있습니다. 웹 화면과 라우터는 `modules/job_posts/`, `modules/training_posts/` 등에서 관리합니다.

## 프로필 최종 설계

`public.users`가 없었다는 전제로 최종 구조를 직접 생성합니다. `public.users` 조회·이전·삭제, 과거 프로필 컬럼 변경, 이전 데이터 백업은 수행하지 않습니다.

| 테이블 | 주요 컬럼 | 관계 |
|---|---|---|
| `public.profiles` | `user_id`, `name`, `email`, `desired_jobs`, `skills`, `use_yn` | `user_id` PK, `auth.users.id` FK |
| `public.profiles_certifications` | `id`, `user_id`, 자격증명·발급기관·취득일, `use_yn` | `profiles.user_id` FK, 사용자별 여러 기록 |
| `public.profiles_trainings` | `id`, `user_id`, 교육명·교육기관·수료일, `use_yn` | `profiles.user_id` FK, 사용자별 여러 기록 |
| `public.saved_jobs` | `user_id`, `job_id`, `created_at`, `use_yn` | 프로필과 채용공고, 복합 PK |
| `public.saved_trainings` | `user_id`, `training_id`, `created_at`, `use_yn` | 프로필과 교육공고, 복합 PK |

이름·이메일은 text NOT NULL, `desired_jobs`와 `skills`는 NULL 허용·기본값 없는 text[]입니다. 자격증·교육 기록의 UUID는 `gen_random_uuid()`로 생성하며 이름은 필수이고 공백 이름은 거절합니다. 날짜는 date, `use_yn`은 기본값 Y인 char(1)로 Y/N만 허용합니다. 외래키에는 `ON DELETE CASCADE`를 적용합니다.

`profiles_trainings`는 사용자가 입력하는 **교육 이수 기록**이며 수집한 교육공고나 북마크와 다른 테이블입니다. 생성 코드는 기존 `public.profiles_trainings`를 삭제하지 않습니다.

### Auth와 이름 수정

`profiles/table.py`의 `initialize_profiles()`가 최종 테이블·권한·함수를 준비합니다. 기존 Auth 회원 중 이메일이 있고 프로필이 없는 회원만 초기 반영합니다. 기존 프로필의 이름·목록·이력은 덮어쓰지 않습니다. 이미 있는 테이블의 구조가 다르면 자동 변경하지 않고 중단합니다.

`profiles/profile_functions.sql`은 가입 시 프로필 생성, 이메일 변경 동기화와 원자 저장 RPC를 정의합니다. 사용자가 수정한 이름은 Auth 동기화 때 보존합니다. `PATCH /api/auth/me`는 본인의 이름을 수정하고, `PUT /api/mypage/profile`은 배열·이력을 RPC로 저장합니다. 빠진 이력은 `use_yn='N'`으로 표시합니다. 요청 형식은 [마이페이지 README](../mypage/README.md)를 확인하세요.

프로필 RLS는 본인 상태 조회를 허용하지만 수정과 자격증·교육 CRUD에는 활성 프로필을 요구합니다. `use_yn='N'` 자체가 Auth 인증이나 세션을 삭제하는 기능은 아닙니다. 북마크 RLS는 상위 `table.py`에 별도로 정의되며 본인 행만 접근하도록 제한합니다.

## 상위 table.py의 실행 범위

1. 북마크가 참조할 기존 공고 테이블을 확인합니다.
2. 기존 북마크 값을 메모리에 보관합니다.
3. `profiles.initialize_profiles()`로 최종 프로필 구조·권한·Auth 초기 반영을 준비합니다.
4. `saved_jobs`, `saved_trainings`를 생성하고 북마크 RLS를 설정합니다.
5. 스키마·외래키·프로필 동작·기존 북마크 보존을 검증합니다.
6. 모두 성공하면 커밋하며 실패하면 전체 트랜잭션을 롤백합니다.

공고 테이블 자체를 생성하거나 원티드·고용24를 호출하지 않습니다. 공고 테이블은 각 수집 폴더의 저장 코드로 준비합니다. 북마크 대상은 옵션 → 기존 FK 대상 → 존재하는 후보 순서로 결정합니다. 기존 북마크의 FK를 다른 공고 테이블로 자동 변경하지 않습니다.

채용 수집의 현재 대상은 `public.job_postings`이지만, 기존 북마크는 이전 `job_posting_mj` 등에 연결되어 있을 수 있습니다. `--print-sql`의 기본 채용 참조는 코드상 `job_posting_mj`이므로 새 채용 테이블 기준으로 SQL을 확인하려면 이름을 명시합니다.

```bash
python -m modules.database.table --print-sql --job-table job_postings --training-table training_posting
```

고용24 외부 문자열 ID는 `training_posting.work24_training_id`, 북마크의 `saved_trainings.training_id`는 교육공고 내부 UUID `id`입니다. 두 컬럼은 서로 다른 역할입니다.

## 실행 방법

`.env`의 `DATABASE_URL`을 준비합니다. 연결 문자열이나 키는 문서에 기록하지 않습니다. 수집 폴더와 `profiles/`는 파일 기준 `MODULE_DIR.parents[2]`, 상위 `table.py`는 `MODULE_DIR.parents[1]`에서 프로젝트 루트 `.env`를 찾습니다.

```bash
python -m pip install -r requirements.txt
```

프로필 3개 테이블만 준비:

```bash
python -m modules.database.profiles.table --print-sql
python -m modules.database.profiles.table --dry-run
python -m modules.database.profiles.table
```

프로필과 북마크를 함께 준비:

```bash
python -m modules.database.table --dry-run
python -m modules.database.table
```

`--dry-run`은 생성·초기 반영·검증 후 DB 변경을 롤백합니다. 스키마 생성 명령은 결과 파일이나 백업 파일을 만들지 않습니다. 각 수집 명령은 별도 CSV/JSON·보고서를 작성할 수 있으므로 하위 README를 확인하세요.

원티드 전체 미저장 링크 수집과 저장 없는 3건 확인:

```bash
python -m modules.database.job_posting.collect --all --save
python -m modules.database.job_posting.collect --check
```

네트워크와 DB를 사용하지 않는 로컬 테스트:

```bash
python -m unittest modules.database.profiles.test_profiles_api modules.database.job_posting.test_wanted_crawler modules.database.training_posting.test_work24_api modules.database.training_posting.test_collection -v
```

## 운영 테이블을 보호하는 생성 테스트

프로필 SQL 생성·권한·구조 검증 함수는 테스트 스키마와 테이블 이름을 인수로 받습니다. 운영 이름과 겹치는 테이블은 별도 테스트 스키마에 생성하여 검증하고, 새로 만든 테이블·스키마만 삭제합니다. 운영 `public.profiles_trainings`를 삭제하거나 Auth 계정을 변경할 필요가 없습니다. 테스트 결과 파일을 만들지 않고 메모리 비교와 콘솔 확인만으로 진행할 수 있습니다.
