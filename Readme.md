# 취준 나침반
 
## Quick Start
```
# 의존성 설치
pip install -r requirements.txt

# 실행(백엔드, 프론트)
uvicorn app:app --reload
```

## 프로젝트 구조
```text
career-compass/
├── app.py                      # FastAPI 앱 · 화면 및 API 라우터 연결
├── modules/                    # 기능별 작업 폴더
│   ├── auth/                   # 로그인 · 회원가입(임이레)
│   │   ├── 기존 소스
│   ├── job_posts/              # 공고 조회 (이미정)
│   │   ├── ...    
│   ├── jd_match/               # 준비 상황 비교 (조상은)
│   │   ├── page.py                 # 화면용 파일
│   │   ├── router.py               # API 라우터
│   │   ├── service.py              # 처리 로직용 파일
│   │   └── model.py                # 모델용 파일
│   ├── training_match/         # 교육 추천 (서민석)
│   │   ├── ...
│   └── mypage/                 # 임시 홈 · 마이페이지 · 관심목록 · 내 정보 (임이레)
│       ├── 기존소스
├── shared/                     # 함께 사용하는 코드
│   ├── config.py                   # 공통 설정용 파일
│   ├── database.py                 # DB 연결용 파일
│   └── components/                 # 공통 UI(기존소스)
│       ├── header.py
│       └── menu.py
├── .env                            # 환경변수 값 (Git 제외)
├── .env.example                    # 팀 공유용 환경변수 예시
├── .gitignore
├── Readme.md
└── requirements.txt
```


@@everyone 
가능하면 오늘~내일중으로 진행해주시면 좋을 내용공유드립니다.

 @mjjj_a 11/06확정사안 반영해서 db설계문서(산출물) 초안 만들어주세요. 
 @yiiiiire 11/06확정사안 반영해서 UI/UX 설계 문서(산출물) 초안 만들어주세요 
 @sms261014 오늘 강사님이 공유해주신 무료 AI 모델 교육추천에 적용할 수 있는지 검토하고 알려주세요. 
 
 저는 내일까지 로그인 후에 인증정보 가져오는 공통모듈 만들어서 공유하겠습니다!