from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from modules.mypage.Mypage import page_user, render_member_page

router = APIRouter(tags=["마이페이지"])


@router.get("/main", response_class=HTMLResponse, summary="임시 홈 화면")
def main_page(request: Request):
    return render_member_page("main", page_user(request))


@router.get("/mypage", response_class=HTMLResponse, summary="마이페이지 홈")
def mypage(request: Request):
    return render_member_page("home", page_user(request))


@router.get("/mypage/bookmarks", response_class=HTMLResponse, summary="관심목록 페이지")
def bookmarks_page(request: Request):
    return render_member_page("bookmarks", page_user(request))


@router.get("/mypage/profile", response_class=HTMLResponse, summary="내 정보 페이지")
def profile_page(request: Request):
    return render_member_page("profile", page_user(request))