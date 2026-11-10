# training_posting — 고용24 교육과정 수집 및 저장

현재 위치는 `modules/database/training_posting/`입니다. 이전 `modules/training_posts/`의 데이터 수집·저장 코드를 이 폴더로 옮겼습니다. 상위 구성과 `table.py` 설명은 [database README](../README.md)를 참고하세요.

교육 모델은 [schemas.py](schemas.py)로 이동했습니다. 수집·저장·테스트의 참조와 실행 명령은 `modules.database.training_posting.*`를 사용합니다.

### 이동 후 경로

| 대상 | 현재 기준 |
|---|---|
| 모델·서비스·저장 코드 import | `modules.database.training_posting.schemas`, `.work24_client`, `.save_to_supabase` |
| 테스트 import 및 `patch()` 대상 | 동일한 `modules.database.training_posting.*` 경로 |
| `work24_client.py`, `save_to_supabase.py`의 `.env` 탐색 | `MODULE_DIR.parents[2] / ".env"`: 프로젝트 루트 |
| 수집 결과·응답 캐시 | 이 폴더의 `results/` |
| DB 테이블 정의 | 이 폴더의 `training_posting_mj.sql` |

`collect.py`가 가져오는 서비스의 `MODULE_DIR`도 새 위치이므로 기본 결과 경로는 `modules/database/training_posting/results/`입니다.

고용24의 **국민내일배움카드 훈련과정 API - 목록**을 사용해 8개 직무와 관련된 교육을 수집합니다. 직무별 최대 125개를 선정하고, JSON 파일과 Supabase의 `public.training_posting_mj` 테이블에 저장합니다.

현재 구현은 **명령줄에서 실행하는 수집·검증·저장 기능**입니다. 웹 화면에서 검색하거나 저장하는 기능은 아직 구현하지 않았습니다.

## 1. 파일별 역할과 필요한 이유

| 파일 | 구현한 기능 | 언제 필요한가 |
|---|---|---|
| [schemas.py](schemas.py) | API 응답 항목 설명(`FIELD_DESCRIPTIONS`), 검색 결과 모델(`TrainingSearchResult`), DB 저장 모델(`TrainingPosting`) 정의 | `work24_client.py`, `collect.py`, `save_to_supabase.py`가 공통으로 사용하므로 필수 |
| [work24_client.py](work24_client.py) | 인증키 로딩, 검색 조건 검증, API 요청, XML 파싱, 오류 처리, 원본 항목 확인 | API를 조회할 때 필수. 단독 실행하면 과정명·기관·지역·NCS 조건으로 한 페이지를 검색할 수 있음 |
| [collect.py](collect.py) | 8개 직무 검색, 제목 기반 관련성 판별, 중복 제거, 직무별 수량 배정, 캐시 재사용, 결과·보고서 생성 | 여러 직무를 모아 수집할 때 사용하는 실행 진입점 |
| [save_to_supabase.py](save_to_supabase.py) | JSON 검증, PostgreSQL 연결, 테이블 준비, 데이터 추가·갱신, 저장 후 조회 비교 | Supabase에 저장할 때 필요. 수집 없이 기존 JSON만 저장할 수도 있음 |
| [training_posting_mj.sql](training_posting_mj.sql) | 테이블의 컬럼·타입·기본값·제약조건 정의 | 저장 코드가 읽어 실행하므로 DB 저장 시 필수. 별도로 직접 실행할 필요는 없음 |
| [test_work24_api.py](test_work24_api.py) | XML 파싱, 빈 결과와 API 오류 구분, 검색 조건 검증, 인증키 비노출 테스트 | 개발·검증용. 실제 수집 실행에 필수는 아님 |
| [test_collection.py](test_collection.py) | 컬럼 변환, 관련성 판별, 중복 제거, 교차 직무 배정, 목표 충족 시 중단, 캐시 재개 테스트 | 수집 규칙을 수정할 때 검증용. 실제 수집 실행에 필수는 아님 |
| [.gitignore](.gitignore) | 대용량 응답 캐시와 임시 JSON 파일을 Git 관리에서 제외 | 실행 기능에는 영향이 없지만 생성 파일 관리에 사용 |
| `README.md` | 파일 역할, 실행법, 수집 기준과 결과 설명 | 사용·유지보수 안내용 |

[공통 모델](schemas.py)의 `NCS_CATEGORIES`는 NCS 대분류 코드 설명입니다. **현재 8개 직무 수집기는 이 코드로 분류하지 않고 제목 키워드로 분류**합니다. NCS 조건 검색은 `work24_client.py --ncs`에서 별도로 지원합니다.

### results/ 아래 파일

| 파일·폴더 | 담고 있는 내용 | 용도 |
|---|---|---|
| [training_postings.json](results/training_postings.json) | 최종 선정된 교육을 DB의 9개 컬럼 형태로 정리한 목록 | 실제 저장 데이터 확인. DB 저장 후 발급된 UUID도 반영됨 |
| [validation_report.json](results/validation_report.json) | 직무별 건수, 부족 수량, 검색 이력, 제외 사유, 선정 근거, 기관 분포, 호출 수, DB 저장 결과 | 수집·분류·저장 과정을 검토할 때 사용 |
| [training_response.xml](results/training_response.xml) | `work24_client.py`로 마지막에 검색한 한 페이지의 원본 XML | API가 어떤 필드를 주는지 확인. 최종 전체 선정 목록은 아님 |
| [training_inspection.json](results/training_inspection.json) | 위 페이지의 원본 값과 필드별 존재·누락·빈 값 구분 | API 항목 점검용. 전체 992개의 선정 보고서는 아님 |
| `api_cache/` | 배치 검색 조건별 성공 응답 XML. 수집 시 자동 생성 | `--resume`으로 재개할 때 API 재호출을 줄임. Git에는 포함하지 않음 |
| `training_error.xml` | API가 오류 XML을 보낸 경우의 응답. 오류가 있을 때 생성 | 인증·서비스 오류 확인용 |
| `*.tmp` | 결과 JSON을 교체하기 전에 쓰는 임시 파일 | 정상 저장되면 최종 JSON으로 교체됨 |

`__pycache__/`는 Python이 자동 생성하는 실행 캐시이며 직접 작성하거나 관리할 소스 파일이 아닙니다.

## 2. 실행 흐름

```text
프로젝트 루트의 .env
  ├─ 훈련 API 키 → work24_client.py → 고용24 목록 API → XML 파싱
  │                               ↓
  │                          collect.py
  │                관련성 판별 → 중복 제거 → 직무 배정
  │                               ↓
  │                  results/training_postings.json
  │                  results/validation_report.json
  │
  └─ DATABASE_URL → save_to_supabase.py
                        ├─ training_posting_mj.sql로 테이블 준비
                        ├─ JSON 데이터 추가·갱신 및 비교 검증
                        └─ public.training_posting_mj
```

[공통 모델](schemas.py)은 이 흐름에서 사용하는 데이터 구조를 정의합니다. 웹 기능용 [router.py](../../training_posts/router.py)와 [page.py](../../training_posts/page.py)는 `modules/training_posts/`에 남아 있으며, 이 폴더의 CLI 수집 흐름에는 연결되어 있지 않습니다.

## 3. 실제 API 수집 기준

### 조회 범위와 목표

| 구분 | 실제 적용 기준 |
|---|---|
| 대상 API | 국민내일배움카드 훈련과정 API - 목록 |
| 응답 형식 | XML, `outType=1` |
| 날짜 기준 | **훈련 시작일**. 신청일이나 종료일 기준이 아님 |
| 이번 수집 기간 | 2026-11-09~2027-05-09 |
| 지역·기관 | 배치 수집에서는 특정 지역·기관으로 제한하지 않음 |
| 훈련유형 | 배치 수집에서 추가 유형 필터를 지정하지 않음 |
| 페이지당 요청 건수 | 100개 |
| 조회 순서 | 훈련 시작일 오름차순. 검색어의 첫 페이지를 먼저 확인하고 다음 페이지는 뒤에 조회 |
| 선정 목표 | 직무별 최대 125개, 총 1,000개 |

10,000건을 먼저 무작위로 조회한 후 1,000건을 뽑는 방식은 사용하지 않았습니다. 필요한 직무의 검색을 이어가고, 목표를 채운 직무는 중단하는 방식입니다.

### 직무별 기본 검색어

아래 기준은 `collect.py`의 `JOB_RULES`에 정의되어 있습니다.

| 직무 | 기본 검색어·교육 주제 |
|---|---|
| 개발자 | 백엔드, 프론트엔드, 웹개발, Java, Spring, React, 소프트웨어 개발 |
| 데이터 분석가 | 데이터 분석, SQL, Python 분석, 통계, 시각화, Power BI |
| 인사 | 인사관리, 채용, 노무, 급여, 조직관리 |
| 총무 | 총무실무, 자산관리, 구매관리, 사무행정 |
| 회계 | 재무회계, 세무회계, 전산회계, 전산세무, 결산 |
| 생산관리 | 생산계획, 공정관리, 품질관리, 재고관리, SCM, 생산 ERP |
| 마케팅 | 디지털 마케팅, 퍼포먼스 마케팅, 콘텐츠 마케팅, 광고, CRM |
| 기획자 | 서비스기획, 사업기획, 상품기획, 시장조사, 요구사항 정의 |

### 검색어와 관련성 판별 기준의 차이

검색으로 반환된 과정이 모두 저장되는 것은 아닙니다. 예를 들어 포괄적인 `파이썬`, `ERP`, `기획`으로 검색하더라도, **제목에서 해당 직무의 관련 표현이 확인되는 과정만** 후보로 남깁니다.

| 설정 | 역할 | 예시 |
|---|---|---|
| `JOB_RULES` | 기본 검색어이자 제목 관련성 판별 기준 | 인사관리, 생산 ERP, 사업기획 |
| `SEARCH_ALIASES` | 조회 누락을 줄이기 위한 검색어·표기 변형 | 웹 개발, 자바, 인사, ERP, 경영전략, 고객분석 |
| `MATCH_ALIASES` | 제목에서 관련 주제임을 인정하는 표현 | 인사평가, 품질경영, 경영기획, 사업계획서, 시장분석 |

영문 대소문자, 공백, 특수문자를 제거해 제목과 기준을 비교합니다. 추가로 `인사`와 `ERP/정보관리사`가 함께 나오면 인사 교육으로, `생산`과 `ERP/정보관리사`가 함께 나오면 생산관리 교육으로 인정합니다.

수집 중 확인한 표기 차이를 반영해 기획자에는 경영기획·사업전략·사업계획서·기획서 작성과 시장·고객 분석 등의 관련 교육도 포함했습니다. 적용한 전체 기준은 보고서의 `search_rules`, `search_aliases`, `matching_aliases`에 기록되어 있습니다.

오탐을 줄이기 위한 제외 규칙도 있습니다.

- 총무: 부동산·금융투자·펀드·자산운용 표현이 있는 자산관리 과정은 제외합니다.
- 마케팅: 영상편집·영상제작·모션그래픽 과정은 마케팅·퍼포먼스·CRM 표현이 추가로 있어야 인정합니다.
- 기획자: 위 영상 제작 계열 과정은 서비스기획·사업기획·상품기획·경영기획·요구사항 표현이 추가로 있어야 인정합니다.

**현재 관련성 검증은 제목 기반 자동 규칙입니다.** 상세 교육내용을 사람이 검수하거나 AI가 의미를 평가한 결과가 아니며, 개인의 경력·선수지식·학습 목표에 맞춘 추천 점수도 계산하지 않습니다.

### 중복 제거와 선정

1. `trprId`, `titleLink`, `title`이 없거나 링크 형식이 잘못되면 제외합니다.
2. 날짜는 `YYYY-MM-DD`, `YYYYMMDD`, `YYYY.MM.DD`를 받아 `YYYY-MM-DD`로 변환합니다. 잘못된 날짜나 시작일보다 빠른 종료일은 제외합니다. 선택 날짜가 없는 경우는 `null`을 허용합니다.
3. 같은 훈련과정 ID는 한 건만 유지합니다. 서로 다른 회차가 조회되면 **조회한 회차 중 가장 이른 시작일**을 가진 회차를 우선합니다.
4. 동일 원본 링크의 중복 후보도 제외합니다. 제목이 같아도 훈련과정 ID가 다르면 별도 과정으로 유지합니다.
5. 각 검색 결과는 공통 후보 목록에 모으므로 다른 직무 검색에서 받은 과정도 재사용합니다.
6. 여러 직무에 해당하는 과정은 대표 직무 한 곳에만 배정합니다. 후보가 적은 직무부터 채우며, 다른 후보로 대체할 수 있으면 재배정합니다.
7. 후보 순서를 섞는 시드의 기본값은 42입니다. 재개 시에는 기존 선정 결과를 우선합니다. 전체 API 데이터에서 균등한 무작위 표본을 추출하는 방식은 아닙니다.
8. 직무별 125개를 채우면 해당 직무의 추가 검색을 멈춥니다. 부족한 수량을 다른 직무나 같은 과정의 다른 회차로 채우지 않습니다.

기관·지역별 최대 비율은 별도로 강제하지 않습니다. `center_counts`는 기관 분포를 확인하기 위한 집계입니다.

### API 호출을 줄이는 방법

- 한 번에 100개씩 요청합니다.
- 다른 검색어·직무에서 받은 후보를 공유합니다.
- 같은 실행에서는 동일한 검색 조건의 응답을 메모리에서 재사용합니다.
- `--resume`은 같은 기간의 이전 보고서와 XML 캐시를 읽어 기존 후보를 먼저 재분류합니다.
- 목표가 찬 직무는 중단하고 부족한 직무만 조회합니다.
- API 오류는 0건으로 취급하지 않고 기록한 뒤 수집을 중단합니다.

`--max-calls`는 **실행 한 번의 실제 API 요청 상한**입니다. 데이터 개수나 누적 실행 전체의 호출 상한이 아닙니다. 재개를 여러 번 하면 누적 요청 수는 이 값보다 커질 수 있습니다.

## 4. DB 컬럼 매핑과 저장 정책

| API 항목 | 저장 컬럼 | DB 타입·제약 |
|---|---|---|
| 내부 생성 | `id` | uuid PK, 기본값 `gen_random_uuid()` |
| `trprId` | `training_id` | text NOT NULL |
| `titleLink` | `source_url` | text NOT NULL UNIQUE |
| `title` | `title` | text NOT NULL |
| `subTitle` | `center_name` | text |
| `address` | `center_address` | text. API에 담긴 주소를 그대로 저장 |
| `traStartDate` | `training_start_dt` | date |
| `traEndDate` | `training_end_dt` | date |
| 내부 기본값 | `use_yn` | char(1) NOT NULL DEFAULT 'Y', Y/N만 허용 |

`use_yn`은 이 API의 공식 목록 응답 항목이 아니므로 내부 기본값 `Y`를 설정합니다. 모집 중 여부를 뜻하는 API 값은 아닙니다. DB 저장 전 `id`는 `null`이고 저장 후 실제 발급 UUID를 JSON에 반영합니다.

`save_to_supabase.py`는 다음 순서로 처리합니다.

1. JSON의 컬럼, 필수값, 날짜, 중복, `use_yn`을 검증합니다.
2. 테이블이 없으면 SQL 파일의 정의대로 생성하고 RLS를 활성화합니다. 공개 접근 정책은 별도로 만들지 않습니다.
3. 기존 테이블의 컬럼과 타입이 모델과 다르면 중단합니다. 기존 구조를 자동 삭제·변경하지 않습니다.
4. `source_url`이 같으면 갱신하고 없으면 추가합니다. 기존 UUID와 기존 `use_yn`은 보존합니다.
5. 입력 데이터와 DB 조회 결과를 비교하고 일치해야 커밋합니다. 비교 시 기존 값 보존 대상인 UUID·사용 여부는 제외합니다.

기존의 다른 데이터는 삭제하지 않으므로 반복 실행 시 테이블 전체 건수와 이번 선정 건수가 달라질 수 있습니다. 직무 분류는 별도 DB 컬럼을 추가하지 않고 보고서의 `selection`에 기록합니다.

## 5. 실행 방법

모든 명령은 **프로젝트 루트 `AIO_project1`**에서 실행합니다.

### 환경 설정

```bash
python -m pip install -r requirements.txt
```

프로젝트 루트 `.env`에 값을 설정합니다. 실제 비밀값을 README에 적거나 Git에 올리지 않습니다.

```dotenv
WORK24_API_KEY=인증키값만입력
DATABASE_URL=PostgreSQL연결문자열
```

기존 변수명 `TRAININING_API_KEY`, `TRAINING_API_KEY`도 지원합니다. 여러 변수가 있으면 `WORK24_API_KEY`부터 사용합니다. 연결 문자열의 `/postgres`는 데이터베이스 이름이며 스키마·테이블 이름이 바뀌어도 바꾸지 않습니다.

### API 한 페이지 조회·항목 확인

```bash
python -m modules.database.training_posting.work24_client \
  --keyword 파이썬 --start 20261109 --end 20270509 --page-size 1
```

`--institution`, `--region`, `--ncs`, `--page`, `--page-size`로 조건을 추가할 수 있습니다. 날짜를 생략하면 오늘부터 90일 범위를 사용합니다.

API를 호출하지 않고 응답 항목 설명만 확인하려면:

```bash
python -m modules.database.training_posting.work24_client --list-fields
```

### 직무별 수집과 DB 저장

```bash
python -m modules.database.training_posting.collect \
  --start 20261109 --end 20270509 \
  --quota 125 --max-calls 160 --resume --save-db
```

`--save-db`를 빼면 JSON만 생성합니다. 배치 날짜를 생략하면 한국 시간 기준 오늘부터 181일을 사용합니다. `--output-dir`로 결과 위치를 바꿀 수 있으며, 기본 위치의 같은 이름 JSON은 새 실행 결과로 교체됩니다.

종료 코드는 목표 충족 시 `0`, 정상 수집했지만 수량 부족 시 `2`, API·DB 오류 시 `1`입니다. 수량 부족으로 `2`가 반환되어도 유효한 선정 데이터의 JSON 생성과 `--save-db` 저장은 수행합니다.

### 기존 JSON만 DB에 저장 / 테이블만 준비

```bash
python -m modules.database.training_posting.save_to_supabase
python -m modules.database.training_posting.save_to_supabase --create-only
```

위 명령은 교육 API를 다시 조회하지 않습니다. 다른 JSON을 저장할 때는 `--input 파일경로`를 지정합니다.

### 테스트

```bash
python -m unittest modules.database.training_posting.test_work24_api modules.database.training_posting.test_collection -v
```

테스트는 합성 응답을 사용하며 실제 API 호출이나 DB 저장을 수행하지 않습니다. 이번 구현에서 15개 테스트가 통과했습니다.

## 6. 저장된 결과와 보고서 읽는 방법

2026-11-09 실행의 저장 결과는 다음과 같습니다. 이후 실행 시 달라질 수 있으며 최신 값은 JSON 보고서를 기준으로 확인합니다.

| 직무 | 목표 | 저장 선정 수 |
|---|---:|---:|
| 개발자 | 125 | 125 |
| 데이터 분석가 | 125 | 125 |
| 인사 | 125 | 125 |
| 총무 | 125 | 125 |
| 회계 | 125 | 125 |
| 생산관리 | 125 | 125 |
| 마케팅 | 125 | 125 |
| 기획자 | 125 | 117 |
| 합계 | 1,000 | **992** |

기획자 8개가 부족해 `status=partial`입니다. 지정한 기간·검색 기준의 결과이며, 전체 고용24에 기획자 과정이 117개만 있다는 뜻은 아닙니다. 당시 별도 DB 연결로 992건 전체가 JSON과 일치하고 과정 ID·원본 링크 중복이 없음을 확인했습니다.

| 보고서 필드 | 확인할 내용 |
|---|---|
| `status`, `stop_reason` | 목표 충족 여부와 중단 사유 |
| `date_range`, `quota_per_job`, `target_total` | 조회 기간과 목표 |
| `selected_total`, `job_counts`, `shortages` | 전체·직무별 선정 수와 부족 수량 |
| `search_rules`, `search_aliases`, `matching_aliases` | 적용한 검색·제목 판별 기준 |
| `queries` | 검색어, 페이지, 검색 총 건수, 받은 건수, 새 후보 수의 이력 |
| `rejected_counts` | 현재 실행에서 처리한 제외·중복 사유별 건수. 재개 전 전체 누적 제외 수는 아님 |
| `selection` | 과정별 대표 직무, 관련 직무, 제목에서 일치한 근거 |
| `center_counts` | 선정 교육의 기관별 분포 |
| `api_calls` | 가장 최근 실행의 실제 API 호출 수 |
| `cache_hits` | 현재 실행 중 검색 응답 캐시 적중 수. 후보 선로딩 전체 횟수를 뜻하지는 않음 |
| `api_calls_all_runs` | 같은 기간으로 재개한 수집 실행들의 누적 호출 수. 이번 저장 보고서는 183회 |
| `preflight_api_calls`, `api_calls_including_preflight` | 사전 확인 1회와 이를 포함한 전체 184회 |
| `database` | 저장 여부·이번 검증 건수·테이블 전체 건수. 이번 보고서에는 별도 최종 확인 결과도 포함 |

현재 수집기는 사전 확인 호출 수를 자동 탐지하지 않습니다. 이번 실행의 사전 조회 1회는 검증 과정에서 기록한 값이며 재개 시 이어받습니다.

## 7. 기준을 바꾸려면

| 바꾸려는 내용 | 수정·지정할 곳 |
|---|---|
| 직무별 기본 검색 주제 | `collect.py`의 `JOB_RULES` |
| 추가 API 검색어 | `SEARCH_ALIASES` |
| 제목에서 관련 교육으로 인정할 표현 | `MATCH_ALIASES`, `match_jobs()` |
| 오탐 제외 규칙 | `match_jobs()` |
| 직무별 목표 수·조회 기간·호출 상한 | `--quota`, `--start`, `--end`, `--max-calls` |
| API 요청·응답 구조 | `work24_client.py`, `TrainingSearchResult` |
| 저장 컬럼 | `TrainingPosting`, `normalize_course()`, SQL 파일, 저장 검증 코드와 관련 테스트를 함께 수정 |
| 웹 검색 API·화면 | `modules/training_posts/router.py`, `modules/training_posts/page.py`에 별도 구현 필요 |

공식 API 안내: https://www.work24.go.kr/cm/e/a/0110/selectOpenApiSvcInfo.do?fullApiSvcId=000000000000000000000000000004
