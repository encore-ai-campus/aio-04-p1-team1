from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse

from modules.mypage.Mypage import page_user, render_member_page, router

from modules.mypage import bookmarks_api, resume_api

# 마이페이지 화면과 관련 API를 하나의 상위 라우터로 묶습니다.
router.include_router(bookmarks_api.router)
router.include_router(resume_api.router)

@router.get("/main", response_class=HTMLResponse, tags=["연결 확인"], summary="팀원 메인 화면 연결 전 임시 화면")
def main_page(request: Request):
    user = page_user(request)
    if isinstance(user, RedirectResponse):
        return user
    return render_member_page("main", user)