# profiles — 최종 프로필 설계 생성

`public.users`가 없었다는 전제로 `profiles`, `profiles_certifications`, `profiles_trainings`를 처음부터 최종 구조로 생성합니다. 다른 테이블에서 정보를 이전하거나 기존 컬럼을 변경·삭제하는 코드는 없습니다.

| 파일 | 역할 |
|---|---|
| [table.py](table.py) | 최종 테이블·인덱스·RLS·컬럼 권한 생성, Auth 초기 반영, 구조 검증 및 실행 |
| [profile_functions.sql](profile_functions.sql) | 가입 시 프로필 생성·이메일 동기화 트리거, 프로필 배열·여러 이력의 원자 저장 RPC |
| [profile_checks.py](profile_checks.py) | 실제 DB에서 가입·이름 수정·소유권·RPC·삭제 연쇄 확인. 검증 데이터는 롤백 |
| [test_profiles_api.py](test_profiles_api.py) | 생성 SQL·정책 테스트 및 과거 REST/RPC API 회귀 테스트. 현재 API와 맞지 않는 항목이 있어 보완 필요 |
| [__init__.py](__init__.py) | Python 패키지 설명 |

## 최종 설계

- `profiles.user_id`: UUID PK, `auth.users.id` FK, `ON DELETE CASCADE`. 별도 사용자 ID를 생성하지 않습니다.
- `name`, `email`: text NOT NULL. 초기 이름은 Auth 메타데이터, 이메일은 Auth 이메일에서 읽습니다.
- `desired_jobs`, `skills`: text[]이며 NULL 허용, 기본값 없음.
- 자격증·교육 기록: UUID PK 기본값 `gen_random_uuid()`, `user_id` 필수이며 `profiles.user_id`를 참조합니다. 한 사용자에게 여러 기록을 저장할 수 있습니다.
- 자격증·교육 이름: NOT NULL, 공백 이름 금지. 기관명과 날짜는 NULL 허용.
- 모든 `use_yn`: char(1) NOT NULL DEFAULT 'Y', Y/N CHECK.

사용자가 변경한 이름·기존 배열·이력은 생성 명령을 다시 실행해도 덮어쓰지 않습니다. `initialize_profiles()`는 유효한 이메일이 있는 Auth 회원 중 프로필이 없는 회원만 추가합니다. 이후 가입과 이메일 변경은 트리거가 처리합니다. 이메일이 없는 Auth 계정은 필수 이메일을 만들 수 없어 프로필 초기 생성에서 제외합니다.

## 접근 정책

로그인한 사용자는 자신의 프로필 상태를 조회할 수 있습니다. 이름·희망 직무·역량·use_yn 수정은 활성 프로필에서만 허용하고, 이메일과 user_id 직접 수정은 차단합니다. 자격증·교육 이력의 조회·추가·수정·삭제 역시 **본인의 활성 프로필**이 있어야 합니다.

`use_yn='N'`은 Auth 계정이나 세션을 직접 삭제하는 기능이 아닙니다. API와 RLS에서 보호된 작업을 거절합니다. 비활성 여부를 판별할 수 있도록 본인 프로필 조회는 허용합니다. Auth 동기화는 사용자가 수정한 이름을 보존합니다. 이력의 `use_yn='N'`은 해당 기록의 삭제 표시입니다.

## 실행

프로젝트 루트에서 `.env`의 `DATABASE_URL`로 실행합니다.

```bash
python -m modules.database.profiles.table --print-sql
python -m modules.database.profiles.table --dry-run
python -m modules.database.profiles.table
```

`--dry-run`은 전체 생성·초기 반영·검증 후 DB 변경을 롤백합니다. 별도 백업 또는 테스트 결과 파일은 생성하지 않습니다. 이미 존재하는 테이블이 설계와 다르면 자동 변경하지 않고 중단합니다.

[상위 table.py](../table.py)는 `initialize_profiles()`를 호출하고 북마크 테이블을 함께 생성합니다. 각 실행의 DB 변경은 한 트랜잭션에서 처리합니다.

```bash
python -m modules.database.table --dry-run
python -m modules.database.table
```

`schema_sql()`, `access_sql()`, `verify_schema()`는 테스트용 스키마와 테이블 이름을 인수로 받을 수 있습니다. 운영 테이블과 이름이 겹칠 때는 별도 스키마에서 생성·제약 검증·삭제를 수행해 기존 테이블을 보호할 수 있습니다. Auth 트리거와 저장 RPC는 `public.profiles` 구조에 맞춰 정의되어 있으며 테스트 스키마에 자동 연결하지 않습니다.

## 현재 화면 코드와 DB 함수의 관계

- 이름 수정: [auth/member_store.py](../../auth/member_store.py)의 직접 SQL로 `profiles.name`을 변경합니다.
- 희망 직무·역량: [mypage/profile_api.py](../../mypage/profile_api.py)에서 각각 배열 컬럼을 수정합니다.
- 자격증·교육 이력: [mypage/profile_entries.py](../../mypage/profile_entries.py)의 개별 CRUD로 처리합니다.
- `career_compass_save_profile` RPC: 배열과 여러 이력을 한 번에 저장하는 별도 DB 함수입니다. 전달 목록에서 빠진 기존 이력은 `use_yn='N'`으로 표시하며, 현재 화면 API는 이 함수를 호출하지 않습니다.

전체 관계와 실행 순서는 [database README](../README.md)를 확인하세요.

## 테스트 종류와 현재 상태

`profile_checks.py`는 생성 명령 실행 중 실제 DB 연결에서 호출됩니다. 임시 Auth 사용자 생성, 본인 이름 수정·이메일 직접 수정 차단, RPC 저장·실패 롤백, Auth 이메일 동기화 시 이름 보존, 프로필 삭제 연쇄를 검사합니다. 검증용 변경은 내부 트랜잭션에서 롤백하며, 활성 프로필이 없으면 소유권·RPC 검증 일부는 건너뜁니다. 현재 함수에는 비활성 계정의 모든 접근을 별도로 검사하는 테스트는 없습니다.

`test_profiles_api.py`의 API 테스트는 이전 REST 요청 모의 객체와 RPC 일괄 저장 인터페이스를 전제로 합니다. 현재 Auth·마이페이지의 직접 SQL 방식과 달라 수정이 필요하며, 기존 모의 객체가 DB 접근을 막지 못하는 항목도 있습니다. 2026-11-11 확인에서 11개 중 3개 실패·5개 오류가 있었습니다. 이 결과는 DB 테이블 생성 실패를 뜻하지 않습니다.

생성 SQL·정책만 DB 연결 없이 확인하려면 다음 두 테스트를 실행합니다.

```bash
python -m unittest \
  modules.database.profiles.test_profiles_api.ProfilesAPITests.test_final_schema_does_not_depend_on_legacy_users \
  modules.database.profiles.test_profiles_api.ProfilesAPITests.test_isolated_schema_names_and_inactive_access_policy -v
```

테스트 코드 수정은 이번 문서 정리에 포함하지 않았습니다.

## 운영 테이블 보존과 임시 생성 테스트

기존 `public.profiles_trainings`는 삭제 대상이 아닙니다. 다음은 별도로 수행한 임시 생성 검증 방식이며 CLI가 자동으로 이 이름의 테스트 테이블을 만드는 것은 아닙니다. 테스트에서 같은 `profiles_trainings` 이름이 필요하면 별도의 테스트 스키마에 `profiles2`, `profiles2_certifications`, `profiles_trainings`를 생성합니다. 최종 생성 함수와 동일한 SQL을 사용하여 컬럼·PK·FK·기본값·CHECK·RLS·본인 이름 수정·비활성 접근 차단·삭제 연쇄를 확인한 뒤 해당 테스트 객체만 삭제합니다.

해당 임시 생성 검증에서는 운영 프로필 데이터의 실행 전후 값을 메모리에서 비교했고, 결과 파일을 저장하지 않았습니다. 별도 스키마의 테이블 테스트는 `public`에 설치되는 가입 트리거·RPC의 신규 설치 테스트와 구분합니다. `profile_checks.py`는 생성 명령 실행 중 운영 이름의 트리거·RPC 동작을 롤백 가능한 검증으로 확인합니다.
