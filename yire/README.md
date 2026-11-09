# YIRE 회원·마이페이지 실행

- `modules/auth/`: 회원가입·로그인 화면과 Supabase Auth 인증 처리
- `modules/mypage/`: 마이페이지·관심목록·이력정보
- `yire/app.py`: 위 기능의 별도 실행 앱
- `yire/requirements.txt`, `.env.example`, `.gitignore`: 설치·환경설정·로컬 파일 제외

저장소 루트에서 실행합니다.

```powershell
python -m pip install -r yire/requirements.txt
Copy-Item yire/.env.example yire/.env
# yire/.env에 실제 Supabase 연결 값을 설정한 뒤 실행합니다.
python -m uvicorn yire.app:app --env-file yire/.env --host 127.0.0.1 --port 8000
```

Supabase Auth가 발급한 access/refresh 토큰을 HttpOnly·SameSite=Lax 쿠키에 보관합니다.
인증은 Supabase 사용자 확인 API로 검증하고, 만료된 access 토큰은 refresh 토큰으로 갱신합니다.
로그아웃은 현재 Supabase 세션을 종료하고 쿠키를 삭제합니다. 세션 정보는 앱 메모리나 별도 DB에 저장하지 않습니다.
쿠키는 발급·갱신 시점부터 24시간 유지됩니다. 기존 로그인 쿠키는 호환되지 않으므로 변경 후 다시 로그인합니다.

배포 시 공개 HTTPS 주소에 맞게 SUPABASE_EMAIL_REDIRECT_URL과 Supabase Auth의 Site URL 및 Redirect URLs를 설정합니다.
HTTPS 요청 또는 HTTPS 인증 복귀 주소를 사용하면 인증 쿠키에 Secure가 적용됩니다.
Supabase 테이블과 RLS는 미리 구성되어 있어야 합니다. 앱은 회원 JWT로 REST API에 접근합니다.
실제 비밀번호와 환경변수 파일은 Git에 올리지 않습니다.
저장소 루트의 공통 실행 앱·설정과 다른 팀원 모듈은 변경하지 않았습니다.
