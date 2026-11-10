# job_posting — 원티드 채용공고 수집 및 저장

현재 위치는 `modules/database/job_posting/`입니다. 이전 `modules/job_posts/`의 데이터 수집·저장 관련 파일을 이 폴더로 옮겼습니다. 상위 역할과 사용자 테이블 생성 코드는 [database README](../README.md)를 참고하세요.

## 파일 역할

| 파일·폴더 | 역할 |
|---|---|
| [wanted_crawler.py](wanted_crawler.py) | 공고 HTML 요청, `__NEXT_DATA__` 파싱, 컬럼 변환, 목록 수집·검증 보고서 생성 |
| [schemas.py](schemas.py) | 저장할 채용공고 컬럼을 `WantedJobPost` 모델로 정의 |
| [source.txt](source.txt) | 수집할 원티드 공고 URL 목록 |
| [save_to_supabase.py](save_to_supabase.py) | 결과 JSON 검증, Supabase 테이블 준비, upsert 및 저장 후 검증 |
| [job_posting_mj.sql](job_posting_mj.sql) | `public.job_posting_mj` 테이블 정의 |
| [test_wanted_crawler.py](test_wanted_crawler.py) | 파싱·변환·예외 처리 및 저장 입력 검증. HTML 캐시가 있으면 실제 화면 헤더 대조 |
| [results/job_postings.json](results/job_postings.json) | 수집한 공고 데이터 |
| [results/validation_report.json](results/validation_report.json) | 성공·실패, 누락 필드, 경고, 원본 보조 정보 |

## 이동 후 실행 경로

아래 명령과 소스 코드의 import는 `modules.database.job_posting.*`를 사용합니다. `schemas.py`, `wanted_crawler.py`, `save_to_supabase.py`, 테스트 참조도 이 위치로 통일했습니다.

`save_to_supabase.py`는 `MODULE_DIR.parents[2] / ".env"`로 프로젝트 루트 설정을 읽습니다. 기본 저장 입력은 이 폴더의 `results/job_postings.json`이며, 테이블 정의는 같은 폴더의 `job_posting_mj.sql`을 읽습니다.

## 수집 실행

프로젝트 루트에서 실행합니다. 파이썬 표준 라이브러리만 사용합니다.

```bash
python -m modules.database.job_posting.wanted_crawler https://www.wanted.co.kr/wd/395333
```

목록 전체를 수집하고 결과와 검증 보고서를 저장합니다. `source.txt`의 주석과 빈 줄은 무시하며 중복 URL은 한 번만 수집합니다. 한 공고가 실패해도 나머지는 계속 처리하고, 실패가 있으면 종료 코드는 1입니다.

```bash
python -m modules.database.job_posting.wanted_crawler \
  --source modules/database/job_posting/source.txt \
  --output modules/database/job_posting/results/job_postings.json \
  --report modules/database/job_posting/results/validation_report.json
```

## 컬럼 매핑

| 컬럼 | 처리 |
|---|---|
| id | 정규화한 원본 URL로 UUID v5 생성. 같은 공고 재수집 시 동일한 UUID |
| source_url | 원본 공고 URL |
| title | position |
| company_name | company.company_name |
| region_id | 외부 지역 테이블 UUID 매핑. 없으면 null |
| address | address.full_location. 상세 주소가 없으면 null |
| employment_type | regular → 정규직, contract → 계약직, intern → 인턴. 그 외 null |
| career_type | 원본 신입/경력 플래그를 신입, 경력, 무관, 신입·경력으로 변환. 데이터 부족 시 미확인. 신입이면서 0~1년이면 화면 표시대로 신입 |
| min_experience_months | annual_from × 12. 누락 시 null |
| max_experience_months | annual_to × 12. 100은 상한 없음이므로 null |
| position_detail | intro: 포지션 소개 원문 |
| main_tasks | main_tasks: 주요업무 원문 |
| qualifications | requirements: 자격요건 원문 |
| preferred_qualifications | preferred_points: 우대사항 원문. 비어 있으면 null |
| deadline_type | due_time이 있으면 날짜 지정. 그 외 HTML 마감일 영역의 상시/채용 시 문구로 구분. 알 수 없으면 미확인 |
| deadline_date | due_time에서 원본 달력 날짜를 추출해 YYYY-MM-DD로 저장. DB 타입은 date. 상시/채용 시/미확인은 null |
| status | active → 모집 중, closed → 마감. 그 외 미확인 |

원문은 줄바꿈과 링크 문자열을 유지하고 앞뒤 공백만 제거합니다. 필수 식별 정보 누락, 요청 URL과 HTML 공고 ID 불일치, 잘못된 경력 범위는 실패로 처리합니다.

`id`는 외부에서 수집하는 값이 아닌 내부 생성 값입니다. 기존 DB에서 공고 UUID를 이미 발급하고 있다면 `source_url`로 기존 레코드를 찾아 연결하는 정책이 필요합니다.

`region_id`는 서비스 DB의 외래키라 원티드의 지역 코드로 대체하지 않습니다. 실제 지역 테이블에서 만든 JSON 파일을 `--regions 파일경로`로 전달할 수 있습니다. 키는 `서울 강남구`처럼 원본의 `location district`를 합친 값이고 값은 실제 UUID입니다. 같은 매핑을 `parse_wanted_html` 또는 `crawl_wanted_job`의 `region_ids` 인자로도 전달할 수 있습니다.

마감일은 `deadline_date date`에 저장합니다. 화면에 `2026.11.15`, JSON에 `2026-11-15T00:00:00`이 있으면 `2026-11-15`로 변환합니다. 시간대가 있는 timestamp도 원본에 쓰인 달력 날짜를 유지하며 시간대 변환은 하지 않습니다. 이전 `deadline_at` 컬럼은 수집 모델에서 제거했습니다.

`close_time`은 현재 상태와 불일치하는 사례가 있어 모집 상태 판단에 사용하지 않습니다. 해당 사례는 검증 보고서에 경고를 남깁니다.

## 검증 결과

2026-11-06에 현재 `source.txt`의 35개 URL을 다시 변환했습니다.

- 현재 목록: 고유 공고 35개, 중복 없음 (초기 목록의 392968 중복은 제거됨)
- HTTP 요청 및 파싱: 35개 성공, 실패 0개
- 고용형태: 정규직 33개, 계약직 2개
- 경력: 경력 32개, 신입 1개, 신입·경력 2개
- 마감 유형: 상시 30개, 날짜 지정 5개
- 원본 status: 모두 active
- 지역 UUID: 실제 지역 테이블 매핑이 없어 35개 모두 null
- 최대 경력: 상한 없는 15개는 null
- 마감 날짜: 5개에 YYYY-MM-DD 저장, 상시 공고 30개는 null
- 우대사항: 275453, 296329, 298034, 392968 공고는 원문이 비어 있어 null
- 298034, 392837은 close_time 값이 있지만 status=active. 보고서에 기록

14개의 단위 테스트와 35개 실제 HTML의 화면 헤더 대조 테스트를 통과했습니다. 이번 목록에는 인턴, 마감 공고, 확정 마감 시각 사례가 없어 이 경우는 합성 데이터로 검증했습니다. 향후 변경되는 공고 상태나 사이트 구조까지 보장하지는 않습니다.

```bash
python -m unittest modules.database.job_posting.test_wanted_crawler -v
```

화면 헤더 대조 테스트는 `공고번호.html` 파일을 모은 폴더가 필요합니다. 이번 다운로드 파일이 남아 있는 환경에서는 다음과 같이 재실행할 수 있습니다.

```bash
WANTED_HTML_DIR=/tmp/career_wanted_batch \
python -m unittest modules.database.job_posting.test_wanted_crawler -v
```

저장한 HTML만으로 배치 수집을 재현하려면 수집 명령어에 `--html-dir /tmp/career_wanted_batch`를 추가합니다. 실제 HTML과 결과에는 공고 작성자의 원문이 포함되어 있습니다.


## Supabase 저장

`.env`의 `DATABASE_URL`에 PostgreSQL 접속 문자열을 설정하고 아래 명령어를 실행합니다. Supabase 프로젝트의 Connect → Session pooler에서 문자열을 확인할 수 있습니다.

```bash
python -m pip install -r requirements.txt
python -m modules.database.job_posting.save_to_supabase
```

`public.job_posting_mj`가 없으면 `job_posting_mj.sql`의 스키마로 생성합니다. `deadline_date`의 DB 타입은 `date`입니다. 지역 테이블이 정해지지 않아 `region_id`는 UUID 컬럼만 선언하고 외래키 제약은 아직 연결하지 않았습니다.

기존 테이블이 있다면 원본 URL 기준으로 갱신하며, 기존 ID와 이미 매핑된 지역 UUID는 보존합니다. 테이블의 `deadline_date`가 없거나 `date` 타입이 아니면 중단하므로 기존 테이블의 컬럼을 임의로 삭제하지 않습니다. 저장과 조회 검증은 한 트랜잭션으로 처리하고, 모든 입력 데이터가 조회 결과와 일치해야 커밋합니다. 이 명령어는 크롤링을 다시 수행하지 않고 `results/job_postings.json`을 저장합니다.

새 테이블에는 RLS가 활성화됩니다. 앱에서 데이터를 읽는 권한/정책은 별도로 설정해야 합니다.
