# Railway 배포 안내

취준나침반 FastAPI 서비스를 Railway에 배포할 때 필요한 설정과 확인 절차를 정리한 문서입니다.

## 1. 배포 대상

Railway 서비스의 Root Directory는 프로젝트 루트로 설정합니다. 애플리케이션 진입점은 루트의 `app.py`이며, `jd_match`는 루트 애플리케이션에 등록된 기능 모듈로 동작합니다.

## 2. Start Command

Railway의 Start Command에 다음 명령을 입력합니다.

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

Railway가 할당하는 `$PORT`를 사용해야 외부에서 서비스에 접근할 수 있습니다. 로컬 전용 주소인 `127.0.0.1`로 실행하면 외부 접속이 되지 않습니다.

## 3. Railway Variables

Railway 프로젝트의 Variables에 아래 환경변수를 등록합니다. 실제 키 값은 저장소에 기록하지 않습니다.

| 변수명 | 용도 |
|---|---|
| `DATABASE_URL` | PostgreSQL/Supabase 데이터베이스 연결 |
| `SUPABASE_URL` | Supabase 프로젝트 주소 |
| `SUPABASE_PUBLISHABLE_KEY` | Supabase 클라이언트 인증 |
| `SUPABASE_EMAIL_REDIRECT_URL` | 이메일 인증 완료 후 이동할 Railway HTTPS 주소 |
| `GROQ_API_KEY` | 챗봇·AI 추천 기능 사용 시 필요한 AI API 키 |
| `GROQ_MODEL` | 사용할 AI 모델명(선택) |
| `GEMINI_API_KEY` | Gemini 기반 AI 기능 사용 시 필요한 API 키 |
| `GEMINI_MODEL` | 사용할 Gemini 모델명(선택) |
| `JEV_API_KEY` | 직무 적합도 외부 API 사용 시 필요한 키 |
| `WORK24_API_KEY` | 교육 데이터 수집 시 필요한 고용24 API 키 |
| `ALLOWED_ORIGINS` | 허용할 프론트엔드·배포 도메인 목록 |

## 4. Supabase Redirect URL

배포 도메인이 `https://서비스주소.up.railway.app`인 경우 다음 값을 Railway Variables와 Supabase Auth 설정에 동일하게 반영합니다.

```text
SUPABASE_EMAIL_REDIRECT_URL=https://서비스주소.up.railway.app/
```

Supabase Dashboard의 Authentication URL Configuration에서도 Site URL과 Redirect URLs를 배포 도메인 기준으로 설정합니다.

## 5. 배포 후 점검

1. Railway Deployments에서 빌드와 실행 로그에 오류가 없는지 확인합니다.
2. 배포 URL에서 회원가입·로그인을 확인합니다.
3. 메인 화면에서 챗봇이 열리고 질문에 응답하는지 확인합니다.
4. 채용공고를 저장한 뒤 적합도 분석 결과가 표시되는지 확인합니다.
5. 교육추천 화면에서 추천 카드가 표시되는지 확인합니다.
6. Railway Logs에서 환경변수 누락, 포트 오류, 외부 API 오류가 없는지 확인합니다.

## 6. 로깅 및 모니터링

별도의 로그 수집 시스템을 추가하지 않고 Railway에서 제공하는 기본 로그를 사용합니다.

- 애플리케이션 실행 로그와 오류 로그는 Railway Deployments의 Logs에서 확인합니다.
- 배포 상태, 재시작 여부, 서비스 응답 상태는 Railway의 기본 배포·네트워크 모니터링을 사용합니다.
- 로그에는 API 키, 세션 토큰, 비밀번호 및 개인정보를 출력하지 않습니다.
- 장기 보관이나 고급 분석이 필요한 경우에는 추후 별도 로그 수집 도구를 연동할 수 있습니다.

## 7. 보안 주의사항

- `.env` 파일과 실제 API 키는 Git에 커밋하지 않습니다.
- Railway Variables에는 필요한 서비스만 접근할 수 있도록 최소 권한의 키를 사용합니다.
- 배포 로그에 토큰, 비밀번호, 개인정보가 출력되지 않는지 확인합니다.
