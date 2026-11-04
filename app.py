import streamlit as st
from modules.job_posts.page import render as job_postspage
from modules.jd_match.page import render as jd_matchpage
from modules.training_match.page import render as training_matchpage
from modules.mypage.page import render as mypagepage

st.set_page_config(page_title="Career Compass")

pages = {
    "공고 조회": job_postspage,
    "준비 상황 비교": jd_matchpage,
    "교육 추천": training_matchpage,
    "마이페이지": mypagepage,
}
selection = st.sidebar.radio("메뉴", list(pages))
pages[selection]()
