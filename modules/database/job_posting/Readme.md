# 원티드 채용공고 수집

8개 직무의 공고 검색·전체 수집·샘플 수집·검증을 `collect.py` 한 파일에서 실행합니다. 저장 대상은 `public.job_postings`입니다. 모든 명령은 프로젝트 루트에서 실행합니다.

## 파일별 역할

| 파일 | 역할 |
|---|---|
| [collect.py](collect.py) | 실행 진입점. 직무별 검색 기준, 링크 검색, 상세 수집, 미저장 공고 이어서 수집, 3건 확인, CSV/TXT 출력 |
| [wanted_crawler.py](wanted_crawler.py) | HTML의 `__NEXT_DATA__` 파싱과 URL·본문·경력·주소·마감 날짜 추출. 외부 폴더의 파서에 의존하지 않음 |
| [schemas.py](schemas.py) | `JobPosting` 데이터클래스. 테이블의 17개 컬럼과 선택값 타입 정의 |
| [save_to_supabase.py](save_to_supabase.py) | `.env` 연결 정보 읽기, 데이터·스키마 검증, SQL 실행, INSERT/UPDATE, 저장 후 값 비교. CSV만으로 저장 재시도도 가능 |
| [job_postings.sql](job_postings.sql) | 테이블 생성과 PK·UNIQUE·NOT NULL·CHECK·기본값·RLS 정의 |
| [test_wanted_crawler.py](test_wanted_crawler.py) | 필드 변환, 실행 모드, 미저장 공고만 수집·저장하는 흐름을 네트워크/DB 없이 검증 |
| [source.txt](source.txt) | `## 직무명` 아래 URL을 한 줄씩 적은 입력 목록 |
| `.gitignore` | Python 바이트코드와 과거 캐시 경로를 Git 추적에서 제외 |

`collect_remaining.py`와 `check_collection.py`는 `collect.py`로 통합하고 삭제했습니다. 설명 문자열만 있던 `__init__.py`도 삭제했습니다. Python 3의 namespace package 방식으로 import와 `python -m` 실행이 가능하며, 프로젝트 루트에서 아래 명령을 사용합니다.

## 실행 방법

전체 목록에서 **DB에 없는 공고만** 수집·저장합니다. 처음부터 전체 수집하거나 중단 후 이어서 실행할 때 같은 명령을 사용합니다.

```bash
python -m modules.database.job_posting.collect --all --save
```

직무별 100개 미만인 경우 현재 목록에 있는 공고만 처리합니다. 20건씩 저장하고, 마지막에 DB를 다시 읽어 전체 값을 비교합니다. 이미 저장된 공고는 다시 수집하지 않습니다. 테이블이 없으면 첫 저장 묶음에서 자동 생성합니다.

실제 공고 3건을 **확인만** 합니다. 파일과 DB에는 저장하지 않습니다.

```bash
python -m modules.database.job_posting.collect --check
```

개발자·데이터 분석가·생산관리 공고를 한 건씩 확인합니다. 목록에 해외 주소 확인 공고가 있으면 생산관리 검증에 우선 사용합니다.

링크를 새로 검색하여 `source.txt`를 갱신합니다.

```bash
python -m modules.database.job_posting.collect --links-only
```

기존 목록에서 직무별 10개를 재수집하고 저장합니다. 기존 URL은 UUID를 유지하고 갱신합니다. `--per-job 100`이면 각 직무의 목록을 최대 100개씩 **다시 수집**합니다.

```bash
python -m modules.database.job_posting.collect --samples-only --per-job 10 --save
```

`--save`를 빼면 상세 결과를 CSV/TXT에만 기록합니다. 옵션 없이 실행하면 링크 검색 후 직무별 10개를 수집하고 로컬 결과만 저장합니다. `--replace`는 `--samples-only ... --save`와 함께 사용하여 해당 URL의 행을 삭제 후 재삽입할 때만 사용합니다. 다른 테이블의 참조가 있으면 중단합니다. `--all`과 `--replace`는 함께 사용할 수 없습니다.

원티드를 다시 요청하지 않고 CSV 저장만 재시도합니다.

```bash
python -m modules.database.job_posting.save_to_supabase
```

로컬 테스트(실제 원티드 요청·DB 저장 없음, 2026-11-11 확인에서 12개 통과):

```bash
python -m unittest modules.database.job_posting.test_wanted_crawler -v
```

## 주요 함수와 처리 흐름

`collect.py`의 `RULES`가 검색어·제목 패턴·원티드 직무 태그를 정의합니다. `collect_links()`가 페이지당 20개씩 검색하고, `relevant()`로 관련성을 확인하여 중복 URL을 제거합니다. `read_sources()`는 직무 헤더·URL 형식·중복을 검사합니다.

`crawl_samples()`는 지정한 직무별 개수만 수집합니다. `collect_all()`은 `read_saved()`로 기존 DB 공고를 확인하고, 미저장 링크를 `fetch()` → `parse_job()` → `validate_records()` → `save_records()` 순서로 처리합니다. 각 20건 묶음은 개별 트랜잭션으로 저장·검증하므로 일부 공고에 실패해도 앞서 완료한 저장은 남습니다. 실패 URL은 보고서에 남고 최종 실행은 실패로 표시됩니다. 원인 수정 후 같은 명령으로 이어서 실행할 수 있습니다.

`check_collection()`은 3건을 메모리에서 파싱·검증하고 콘솔에만 출력합니다. HTML 캐시와 검색 응답 JSON 파일은 모든 모드에서 생성하지 않습니다.

## 데이터 처리 규칙

- `job_name`: 제목 패턴 또는 원티드 직무 태그로 확인한 8개 직무 중 하나. 직무 간 중복 URL은 먼저 선정한 직무에 배정합니다.
- `region_name`: 시·도와 시·군·구를 사용합니다. 해외 공고처럼 상세 주소만 있으면 실제 `full_location`을 사용하며, 주소가 전혀 없으면 오류로 처리합니다.
- 경력: 연 단위 정수로 저장합니다. **신입의 `max_experience_years`는 NULL**, 신입·경력 혼합과 경력 공고는 원본 범위를 유지합니다. 최대 제한 없음(원본의 100)은 NULL입니다.
- `deadline_date`: DB 타입은 **date**, CSV는 `YYYY-MM-DD`입니다. 원본의 달력 날짜를 유지하며 마감일이 없으면 NULL입니다.
- `id`: 최초 저장 시 DB에서 UUID를 생성합니다. `source_url` 기준 갱신 시 기존 UUID를 유지합니다.
- DB 구조·필수값·제약과 저장 값을 검증하며 다른 스키마로 임의 변경하지 않습니다. 신입 최대 경력 NULL 규칙은 수집·저장 코드에서 적용하고 검증합니다.

`job_postings.sql` 하나에 최종 테이블 설계를 정의합니다. 처음부터 `deadline_date date`로 생성하며 별도 마이그레이션 SQL은 사용하지 않습니다. 저장 코드는 테이블이 없을 때 이 파일을 실행하고, 이미 있으면 최종 설계와 일치하는지만 검증합니다. 구조가 다르면 자동 변경하지 않고 중단합니다. 신규 테이블에는 RLS를 활성화하고 `service_role` 권한을 설정하며 일반 사용자용 조회 정책은 별도로 정의해야 합니다.

## 결과 파일

| 경로 | 내용 |
|---|---|
| `results/job_postings.csv` | 수집 결과와 DB 저장 UUID. 빈 칸은 NULL |
| [results/search_report.txt](results/search_report.txt) | 직무별 링크 수, 실제 사용한 검색어와 조회 페이지 내역 |
| [results/validation_report.txt](results/validation_report.txt) | 오류·NULL 필드·직무별 건수·DB 검증 결과 |
| `results/backups/` | 전체 수집 시작 전 기존 CSV·검증 보고서 백업 |

결과는 실행 범위에 맞게 갱신됩니다. 전체 수집 후 샘플 수집을 실행하면 결과 파일도 샘플 범위로 바뀝니다. `--check`는 결과 파일을 변경하지 않습니다.

2026-11-11 수집 완료 당시 개발자·데이터 분석가·인사·회계·마케팅·기획자는 각각 100개, 총무는 70개, 생산관리는 38개로 총 **708개**였습니다. 신입 54개의 최대 경력은 모두 NULL, 마감 날짜가 있는 공고는 90개였습니다. 이는 당시 검증 기록이며 현재 DB를 다시 조회한 값은 아닙니다. 보고서의 `previously_saved`와 `newly_saved`는 마지막 실행 한 번의 건수입니다.

## 추가로 합칠 수 있는 파일

`schemas.py`의 `JobPosting`을 `wanted_crawler.py`에 넣어 파일 하나를 더 줄일 수 있습니다. 현재는 파서와 DB 저장 코드가 함께 사용하는 데이터 구조를 찾기 쉽도록 유지했습니다. 모델을 합치면 저장 코드도 모델을 읽기 위해 파서 모듈에 의존하게 됩니다.

테이블 SQL은 `job_postings.sql`로 통합했습니다. 파싱 코드와 DB 저장 코드는 변경 이유와 테스트 범위가 달라 분리해 두었습니다.

## 다른 database 모듈과의 구분

이 폴더는 채용공고의 생성·수집·저장만 담당합니다. 웹 채용공고 조회·필터·하트 저장 연동은 [job_posts README](../../job_posts/README.md)를 확인하세요. 수집기가 사용하는 DB 연결과 로그인 사용자의 조회·북마크 API는 별도 실행 경로입니다.

사용자 프로필과 교육 이수 기록의 생성은 [profiles README](../profiles/README.md), 프로필·북마크 통합 실행은 [database README](../README.md)를 확인하세요. `job_postings.sql`은 최종 date 구조를 직접 생성하며 프로필 테이블을 변경하지 않습니다.


## 매일 마감 상태 갱신

[update_deadlines.py](update_deadlines.py)는 한국 시간 기준 오늘 날짜가 `deadline_date`보다 늦은 행을 `use_yn='N'`으로 변경합니다. 마감 당일과 NULL 마감일은 유지하고, 이미 N인 행을 Y로 되돌리지 않습니다. DB 스키마 변경이나 공고 재수집은 하지 않습니다.

프로젝트 루트에서 기존 가상환경을 활성화하고 실행합니다. 루트 `.env`의 `DATABASE_URL`과 `shared.database.get_db` 연결을 사용합니다.

```bash
# 변경 대상 건수 확인: UPDATE 후 전체 롤백
python -m modules.database.job_posting.update_deadlines --dry-run

# 실제 반영: 매일 한 번 실행
python -m modules.database.job_posting.update_deadlines
```

실행하는 SQL의 조건은 다음과 같습니다.

```sql
UPDATE public.job_postings
SET use_yn = 'N'
WHERE use_yn = 'Y'
  AND deadline_date IS NOT NULL
  AND (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Seoul')::date > deadline_date;
```

이 명령은 실행한 시점에만 적용됩니다. 자동 스케줄러는 등록하지 않았습니다. 공고 데이터를 다시 저장해 Y로 갱신한 경우에는 이 명령을 다시 실행하면 됩니다. 웹의 ‘마감된 정보 제외’는 날짜도 비교하므로 일일 갱신 전이라도 지난 공고를 제외합니다.
