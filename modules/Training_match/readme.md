# 교육추천 — 채용공고와 본인 프로필 비교
## 채용공고·내 프로필 매칭 (2026-11-09)
- 로그인한 회원이 교육추천 화면에서 채용공고를 선택하고 추천받기를 누릅니다.
- public.job_posting_mj: 공고 ID로 업무·자격요건·우대사항 조회
- public.profiles_LYR: 로그인 회원의 user_id와 Supabase JWT/RLS로 본인 프로필만 조회
- public.training_posts_sms: 저장된 교육 480개에서 조건에 맞는 후보 선정
- Groq가 공고 요구 역량과 자격증·이수 교육을 비교하여 최대 3개 교육과 짧은 추천 이유를 반환
- 희망 직무는 보유 능력으로 간주하지 않고, 이수 교육만으로 숙련도나 경력을 단정하지 않습니다.
- 프로필 항목이 모두 비어 있으면 마이페이지 등록을 안내합니다.
- 공고와 프로필을 직접 입력하는 방식 및 가상 예시 버튼을 제거했습니다.
- 이름·이메일·회원 ID는 Groq에 보내지 않습니다. 추천 버튼을 누를 때 필요한 학습/공고 정보만 전송합니다.
- 공고·프로필 원본과 교육 저장 자료를 수정하거나 자동 갱신하지 않습니다.
- 공고 마감 여부는 선택창 안내에서 확인하세요. 공고 상태만으로 현재 지원 가능 여부를 보장하지 않습니다.

### 연결 경로
- GET /training_match : 로그인한 회원의 추천 화면 (미로그인 시 /signin)
- GET /training_match/api/context : 공고 목록과 본인 프로필 요약
- POST /training_match/api/recommendations : {job_id, goals?, budget?, mode?}
- /training_match?job_id=<공고 UUID> 로 이동하면 해당 공고를 선택합니다.
- 클라이언트가 보내는 user_id, 임의 공고 내용, 타인 프로필은 허용하지 않습니다.
- 라이브러리 추가/제거 없음. 기존 requirements.txt 유지.

실행: 프로젝트 루트에서 `.\.venv\Scripts\python.exe -m uvicorn app:app --host 127.0.0.1 --port 8000`
주소: http://127.0.0.1:8000/training_match (회원 로그인 필요)
환경변수는 기존 루트/모듈 .env를 그대로 읽습니다. shared에 키 값을 추가하지 않았습니다.

### 프로필 매칭 검증 결과
- 실제 job_posting_mj 공고 35개 조회 및 profiles_LYR 프로필 2개 구조 확인
- 실제 DB 공고 + 검증용 가상 프로필 + 저장 교육 480개로 Groq 호출 성공, 교육 2개 추천
- 검증 과정에서 실제 회원 프로필은 Groq에 전송하지 않음
- JWT와 본인 user_id 필터 적용, 미로그인 요청 차단, 타인 user_id/임의 skills 요청 거부 검사 통과
- 없는 공고/빈 프로필/DB 오류 안내, JavaScript 문법 및 기존 통합 검사 통과
- 실제 회원 로그인 세션으로 끝까지 진행하는 화면 검증은 수행하지 않음
- 검사 실행: `.\.venv\Scripts\python.exe tests\verify_integration.py`
