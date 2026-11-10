# 교육목록

통합 서버에서 작동하도록 기존 router/page/service/model 구조로 구성했습니다.
- router.py: 화면 및 API 경로
- page.py: 기존 디자인과 화면 동작
- service.py: 저장된 교육 데이터의 화면 형식 변환
- model.py: DB 모델 없음
- .env: API 키 설정 (실제 값은 공유하거나 Git에 올리지 않습니다.)

루트에서 `python -m uvicorn app:app --host 127.0.0.1 --port 8000` 실행 후
http://127.0.0.1:8000/training_posts 에 접속합니다.
서버 진입점은 프로젝트 루트 app.py 하나이며, 이 모듈은 router.py로 연결됩니다.
교육 데이터 및 추천 결과는 DB에 저장하지 않습니다.


## 교육목록 DB 연결 (2026-11-10)
교육목록과 추천은 다른 담당자가 관리하는 public.training_posting_mj를 읽기 전용으로 조회합니다.
shared.database.get_db()를 사용하며 교육 모듈의 트랜잭션은 SET TRANSACTION READ ONLY로 제한합니다.
테이블 생성·변경·추가·수정·삭제 및 외부 API 자료 수집/저장은 수행하지 않습니다.
기존 저장 함수와 import_training_posts.py는 제거했습니다.

- id: 화면 식별 키, training_id: 과정 ID, source_url: 원문 링크
- title: 교육명, center_name: 교육기관, center_address: 주소
- training_start_dt / training_end_dt: 교육 기간
- use_yn='Y'인 교육만 표시하며, 시작일 미정인 교육도 포함합니다.
- 날짜 범위는 기본적으로 오늘 전후 365일이며 시작일을 기준으로 조회합니다.
- 분야·교육비·교육 방식·회차 정보는 미제공으로 표시합니다. 제목에서 추출한 기술 태그는 DB 분야로 간주하지 않습니다.
- 기본 검색 및 추천은 분야·비용·방식 제한 없이 진행합니다. 비용/방식 제한을 명시하면 미확인 교육은 제외합니다.
- 표시 시각은 저장 시각이 아닌 조회 시각입니다.
- 서버 실행: 프로젝트 루트에서 `python -m uvicorn app:app --reload`
