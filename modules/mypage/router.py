from modules.mypage.Mypage import router

from modules.mypage import bookmarks_api, profile_api

# 마이페이지 화면과 관련 API를 하나의 상위 라우터로 묶습니다.
router.include_router(bookmarks_api.router)
router.include_router(profile_api.router)
