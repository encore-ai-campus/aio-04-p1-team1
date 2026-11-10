# 취준나침반 공통 컴포넌트

기존 앱 파일을 수정하지 않고 추가한 공유용 파일입니다.
compass-preview.html을 직접 열어 헤더/메뉴/글꼴을 확인하세요.

- compass-header.html : 헤더 조각 (이름/현재 메뉴는 렌더러가 채움)
- compass-sidebar.html : 접이식 메뉴와 준비 중 안내창
- styles/compass.css : 공통 색상 변수, 규격, 글꼴 (브랜드 600 / 그 외 400)
- scripts/compass.js : 기존 메뉴 동작/준비 중 안내/로그아웃 UI 동작
- fonts/A2Z-Regular.woff2 : 제공받은 에이투지체 4Regular
- fonts/A2Z-SemiBold.woff2 : 제공받은 에이투지체 6SemiBold
- compass.py : Python HTML 문자열에서 공통 파일을 사용하는 함수

## Python 사용 예시 (기존 코드에 자동 적용하지 않았습니다):

```python
from shared.components.compass import apply_member_shell

html = """<!doctype html><html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>__CC_CSS__</style></head><body class="cc-member-page">
__CC_HEADER____CC_MENU__
<main class="cc-page" data-member-content>페이지별 본문</main>
__CC_SCRIPT__</body></html>"""
html = apply_member_shell(html, authenticated_user, current="main")
# current="mypage"이면 마이페이지가 현재 메뉴로 표시됩니다.
# authenticated_user는 서버에서 인증한 사용자(dict, name 포함)를 전달합니다.
```

이 렌더러는 CSS/JS/글꼴을 HTML에 포함하므로 app.py에 static 연결을 추가할 필요가 없습니다.
HTML 조각만 직접 열면 완성된 화면이 아니므로 미리보기 파일을 여세요.
JS는 기존 /api/auth/signout 엔드포인트를 호출합니다. 인증 API 자체는 변경하지 않습니다.
기존 member_shell.py와 동시에 중복 적용하지 마세요. 사용할 페이지에서 공통 함수로 연결해야 합니다.
페이지별 기존 CSS에 별도 font나 font-weight 선언이 있으면 공통 글꼴 적용 여부를 확인하세요.
실제 로그인/회원가입/마이페이지에 자동 적용하지 않았습니다.
글꼴 사용/재배포 조건은 제공받은 원본 글꼴 배포처의 라이선스를 따릅니다.

## 데이터베이스 마이그레이션

`migration.py`는 사용자, 프로필, 저장한 공고, 저장한 교육 테이블을 생성하고
Supabase Auth의 `auth.users` 정보를 `public.users`에 동기화합니다.

프로젝트 루트에서 실행합니다.

```bash
python -m shared.migration --print-sql
python -m shared.migration
```

기본 외래키 대상은 `job_posting_mj`, `training_posting_mj`입니다. 다른 테이블을
사용하려면 `--job-table`과 `--training-table` 옵션을 지정합니다.
마이그레이션은 기존 테이블의 구조와 외래키를 먼저 검증하며, 검증에 실패하면
트랜잭션을 롤백합니다. 실제 실행에는 `.env`의 `DATABASE_URL`이 필요합니다.

## 인증 의존성

`auth_dependencies.py`는 FastAPI 라우터에서 인증된 사용자를 일관된 `User` 모델로
받기 위한 의존성을 제공합니다.

```python
from shared.auth_dependencies import CurrentUser

@router.get("/my-data")
def my_data(user: CurrentUser):
    return {"user_id": str(user.id), "name": user.name}
```

`CurrentUser`는 요청의 인증 상태를 확인하고 `id`, `name`, `email`을 가진 `User`
객체를 주입합니다. 인증되지 않은 요청은 인증 계층에서 처리됩니다.
