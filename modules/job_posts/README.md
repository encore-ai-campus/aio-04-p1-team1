# job_posts — 로그인 회원의 채용공고 검색 화면

접속 주소는 **`/job_posts`**입니다. 프로젝트 루트에서 `uvicorn app:app --reload`로 실행한 뒤 로그인 상태로 접속합니다. 기존 `app.py`가 이 폴더의 `router`를 이미 등록하므로 별도 앱 설정은 필요하지 않습니다.

## 구현 기능

- 기존 Supabase Auth 로그인 쿠키를 사용합니다. 화면 요청이 미인증이면 `/signin`으로 이동하고 검색 API는 401을 반환합니다.
- `public.job_postings`의 사용 중인 공고(`use_yn='Y'`)를 조회합니다.
- 직무/분야·지역·경력·고용형태를 조합하고, 기업명·공고 제목·직무명으로 키워드를 검색합니다.
- 회사명·제목·직무·지역·경력·고용형태·마감일·하트 저장 상태를 카드에 표시합니다.
- 카드와 상세 보기 링크는 원티드 원문을 새 탭에서 엽니다. 원티드 HTTPS 공고 URL만 링크로 허용합니다.
- 하트는 기존 `/api/bookmarks` API로 `saved_jobs`에 저장하거나 취소합니다. 취소는 기존 API의 `use_yn='N'` 정책을 따릅니다.
- 페이지네이션, 검색 조건 초기화·태그 해제, 로딩·빈 결과·오류·저장 알림을 제공합니다.
- ‘내 이력과 비교하기’는 기존 `/jd_match/{공고 UUID}` 화면으로 연결합니다.

## 파일별 역할

| 파일 | 역할 |
|---|---|
| [router.py](router.py) | 화면과 검색 API 라우트, 인증 확인, DB 오류 응답 |
| [search_models.py](search_models.py) | 검색 조건·응답 모델, 입력 길이·페이지·정렬 값 검증 |
| [job_repository.py](job_repository.py) | 필터 선택지·조건 검색·결과 수·본인 저장 상태를 조회하는 매개변수 SQL |
| [search_page.py](search_page.py) | HTML·CSS·JS를 읽고 공통 회원 디자인으로 렌더링 |
| [templates/job_search.html](templates/job_search.html) | 검색 패널·검색창·카드 목록·페이지 이동·알림의 HTML 구조 |
| [assets/job_search.css](assets/job_search.css) | 화면 배치, 카드·하트·태그 스타일, 좁은 화면 대응 |
| [assets/job_search.js](assets/job_search.js) | 검색 요청·URL 조건 복원·페이지 이동·안전한 DOM 렌더링·하트 저장/취소 |
| [test_job_search.py](test_job_search.py) | 실제 네트워크/DB 없이 인증·SQL 조건·응답·오류를 검증하는 9개 테스트 |

내용이 없던 `model.py`, `page.py`, `service.py`는 역할이 명확한 위 파일들로 대체했습니다. 수집 코드는 이 폴더에 포함하지 않으며 [database/job_posting](../database/job_posting/README.md)에서 관리합니다.

## 공통 기능 재사용

`shared/components/compass.py`의 `apply_member_shell()`을 호출하여 공통 헤더·메뉴·팔레트·A2Z 폰트를 그대로 사용합니다. 별도 CSS/JS 서버나 정적 파일 mount 없이 화면 렌더링 시 포함합니다. 공통 사이드바의 ‘공고모음’과 메인 화면의 ‘공고 전체 보기’가 `/job_posts`로 연결됩니다. 공고 화면에서는 공통 메뉴가 현재 페이지로 표시됩니다.

인증은 `shared.auth_dependencies.CurrentUser`, DB 연결은 `shared.database.get_db`를 사용합니다. 사용자 ID는 요청 본문이나 검색 조건으로 받지 않습니다. 북마크는 `modules/mypage/bookmarks_api.py`와 `bookmarks_store.py`의 기존 저장·소유권·RLS 처리를 재사용합니다. 브라우저에 DB 연결 정보나 서비스 키를 전달하지 않습니다.

## 검색 API

| 주소 | 기능 |
|---|---|
| `GET /job_posts` | 로그인 회원 검색 화면 |
| `GET /job_posts/api/filters` | DB에 존재하는 직무·광역 지역·고용형태 선택지 |
| `GET /job_posts/api/jobs` | 조건 검색과 페이지별 저장 여부 |

검색 파라미터:

| 이름 | 설명 |
|---|---|
| `q` | 기업명·제목·직무 키워드, 최대 100자. `%`, `_`는 와일드카드가 아닌 글자로 처리 |
| `job` | 직무명 일치 |
| `region` | 지역 첫 단어 일치. `수도권`은 서울·경기·인천 |
| `career` | `신입`, `경력`, `무관`, `신입·경력` 중 하나. 신입/경력 지원 가능은 혼합·무관 공고도 포함 |
| `employment` | `employment_type` 컬럼 값 일치 (정규직·계약직·인턴 등) |
| `exclude_closed` | 기본 true. 한국 날짜 기준 지난 마감일 제외, 마감일 NULL은 포함 |
| `sort` | `default`, `deadline`, `company`. 등록일 컬럼이 없어 최신순은 제공하지 않음 |
| `page`, `size` | 기본 1페이지·8개. size는 최대 40 |

기본순과 회사명순은 회사명·제목·UUID 순서로 안정적으로 정렬합니다. 마감임박순은 마감 날짜가 있는 공고를 우선합니다. 비활성 공고는 항상 제외하며 ‘마감된 정보 제외’를 해제하면 사용 중인 공고 중 날짜가 지난 공고도 표시합니다.

## 실행·검증

```bash
uvicorn app:app --reload
python -m unittest modules.job_posts.test_job_search -v
```

실제 DB에서 공고 목록·조건 조합 검색과 기존 북마크 저장·조회·취소를 확인했습니다. 북마크 검증은 전체 롤백하여 기존 데이터를 보존했습니다. 브라우저 화면은 별도 테스트 데이터로 카드·검색·빈 결과·초기화·하트·페이지 이동을 확인했습니다. 운영 화면은 테스트 데이터 대신 실제 API를 호출합니다.
