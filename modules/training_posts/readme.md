# 교육목록

통합 서버에서 작동하도록 기존 router/page/service/model 구조로 구성했습니다.
- router.py: 화면 및 API 경로
- page.py: 기존 디자인과 화면 동작
- service.py: 고용24 API 처리
- model.py: DB 모델 없음
- .env: API 키 설정 (실제 값은 공유하거나 Git에 올리지 않습니다.)

루트에서 `python -m uvicorn app:app --host 127.0.0.1 --port 8000` 실행 후
http://127.0.0.1:8000/training_posts 에 접속합니다.
app.py는 중복 처리 코드가 없는 호환용 진입점입니다.
교육 데이터 및 추천 결과는 DB에 저장하지 않습니다.


## 교육목록 Supabase 저장 방식 (2026-11-09 변경)
교육모음은 public.training_posts_sms에 저장된 자료만 읽습니다.
대분류 24개별 최신 훈련 시작일순 최대 20개, 총 최대 480개를 저장합니다.
동일 기관·과정·회차는 중복 저장하지 않으며 같은 교육은 기존 ID를 유지해 갱신합니다.
API 조회가 일부 실패하거나 DB 저장·건수 검증에 실패하면 전체 저장을 취소하고 기존 자료를 유지합니다.
자동 갱신, 서버 시작 시 수집, 예약 작업, 화면 업데이트 버튼은 없습니다.
검색/조건 적용/초기화는 DB 재조회이며 고용24 API를 호출하지 않습니다.
필요할 때만 프로젝트 루트에서 명시적으로 다음 명령을 실행할 수 있습니다.
```powershell
.\.venv\Scripts\python.exe import_training_posts.py
```
조회 범위는 실행일 기준 전후 365일이며, 최신 기준은 등록일이 아닌 교육 시작일입니다.
분야별 실제 조회 결과가 20개 미만이면 존재하는 자료만 저장합니다.
DB 접속은 루트 .env의 DATABASE_URL과 TRAINING_DB_SSLROOTCERT를 사용합니다.
인증서와 호스트 이름을 검증하며, Windows DLL 제한을 피하기 위해 pg8000==1.31.6을 requirements.txt에 추가했습니다.
교육추천은 이번 변경 대상이 아니며 기존대로 고용24/Groq API를 직접 사용합니다.
