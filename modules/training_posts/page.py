"""교육목록 HTML/CSS/JavaScript 화면."""

import re
from pathlib import Path

from shared.components.compass import apply_member_shell


# Match the main page's type scale without replacing the shared A2Z font.
TRAINING_TYPOGRAPHY = r"""
body.cc-member-page.cc-training-page{font-size:14px}
.cc-training-page .cc-brand,.cc-training-page .cc-brand span{font-size:24px}
.cc-training-page .cc-top-button{font-size:12px}
.cc-training-page .cc-member-name,.cc-training-page .cc-shell-message{font-size:12px}
.cc-training-page .cc-menu-heading,.cc-training-page .cc-menu-heading span{font-size:18px}
.cc-training-page .cc-menu-label{font-size:10px}
.cc-training-page .cc-menu-item{font-size:14px}

.cc-training-page .cc-soon{font-size:9px}
.cc-training-page .cc-menu-note{font-size:11px}
.cc-training-page .cc-service-dialog h2{font-size:20px}
.cc-training-page .cc-service-dialog p{font-size:13px}
.cc-training-page .cc-dialog-confirm{font-size:12px}
.cc-training-page .cc-page-heading .eyebrow{font-size:10px}
.cc-training-page .cc-page-heading h1{font-size:29px}
.cc-training-page .cc-page-heading>p:last-child{font-size:13px}
.cc-training-page :is(.results-head h2,.rec-heading h2,.rec-certificates h2){font-size:20px}
.cc-training-page :is(.sidebar h2,.rec-panel h2){font-size:17px}
.cc-training-page :is(.card h3,.rec-card h3,.certificate-card h3){font-size:15px}
.cc-training-page :is(.provider,.card-meta,.rec-meta){font-size:10px}
.cc-training-page :is(.badge,.chip,.tags,.learning-badge,.certificate-label){font-size:9px}
.cc-training-page :is(.details,.rec-detail){font-size:10px}
.cc-training-page :is(.field>span,.ai-form label){font-size:12px}
.cc-training-page :is(select,.search input,.ai-form input,.ai-form textarea){font-size:12px}
.cc-training-page :is(.apply,.search button,.ai-submit){font-size:14px}
.cc-training-page :is(.reset,.analysis-button){font-size:11px}
.cc-training-page :is(.sort select,.rec-condition,.gap-line,.gap-pill){font-size:12px}
.cc-training-page .training-posts-content .ai-recommend-link{display:inline-flex;align-items:center;justify-content:center;min-height:46px;padding:10px 24px;font-size:calc(12px + 3pt);white-space:nowrap;background:#fff;border:1px solid #000}
.cc-training-page :is(.rec-reason,.certificate-card p,.analysis-summary,.gap-explanation){font-size:12px}
.cc-training-page :is(.sidebar-note,.catalogue-note,.rec-footnote,.input-hint){font-size:10px}
.cc-training-page .pagination button{font-size:12px}

.cc-training-page footer{font-size:10px}
.cc-training-page footer span:last-child{font-size:9px}
@media(max-width:1100px){.cc-training-page :is(.card h3,.rec-card h3){font-size:16px}}
@media(max-width:820px){
  .cc-training-page .cc-brand,.cc-training-page .cc-brand span{font-size:20px}
  .cc-training-page .cc-member-name,.cc-training-page .cc-top-button{font-size:11px}
  .cc-training-page .cc-page-heading h1{font-size:25px}
  .cc-training-page .cc-page-heading>p:last-child{font-size:12px}
  .cc-training-page :is(.provider,.card-meta,.rec-meta){font-size:11px}
  .cc-training-page :is(.results-head h2,.rec-heading h2,.rec-certificates h2){font-size:19px}
}
@media(max-width:620px){
  .cc-training-page .cc-member-name{font-size:10px}
  .cc-training-page .cc-page-heading h1{font-size:23px}
}
"""


def render_training_page(template, user, current):
    """Use the shared shell and connect its existing training menu entries."""
    rendered = apply_member_shell(template, user, current=current)
    if current == 'training_posts':
        bookmarks = (Path(__file__).resolve().parents[2] / 'shared/components/scripts/bookmarks.js').read_text(encoding='utf-8')
        rendered = rendered.replace('</head>', '<script>' + bookmarks + '</script></head>', 1)
    rendered = rendered.replace('</head>', '<style>' + TRAINING_TYPOGRAPHY + '</style></head>', 1)
    routes = {"training": "training_match", "courses": "training_posts"}

    def connect_menu(match):
        route = routes[match.group(1)]
        content = re.sub(r'<span class="cc-soon">.*?</span>', '', match.group(2), flags=re.S)
        selected = ' aria-current="page"' if route == current else ''
        return f'<a class="cc-menu-item" href="/{route}"{selected}>{content}</a>'

    rendered = re.sub(
        r'<button class="cc-menu-item" type="button" data-cc-pending="(training|courses)">(.*?)</button>',
        connect_menu, rendered, flags=re.S,
    )
    if current in routes.values():
        rendered = rendered.replace(f'href="/{current}">',
                                    f'href="/{current}" aria-current="page">')
    return rendered


PAGE = r"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>교육모음 · 취준나침반</title>
<meta name="description" content="고용24 내일배움 교육을 분야, 방식, 교육비로 찾아보고 관심목록에 저장하세요.">
<style>.training-posts-content{--ink:var(--cc-text);--muted:var(--cc-muted);--line:var(--cc-border);--paper:var(--cc-background);--yellow:var(--cc-yellow);--green:#7d9970;--pale:#edf3e7;box-sizing:border-box}
.training-posts-content *{box-sizing:border-box}
.training-posts-content button,.training-posts-content input,.training-posts-content select{font:inherit;color:inherit}
.training-posts-content button,.training-posts-content select{cursor:pointer}
.training-posts-content button{touch-action:manipulation}
.training-posts-content a{color:inherit;text-decoration:none}
.training-posts-content button:disabled{cursor:default;opacity:.35}
.training-posts-content button:focus-visible,.training-posts-content a:focus-visible,.training-posts-content input:focus-visible,.training-posts-content select:focus-visible{outline:3px solid #c99c1c;outline-offset:4px}
.training-posts-content .layout{display:grid;grid-template-columns:minmax(0,1fr);gap:30px;align-items:start}
.training-posts-content .sidebar{background:#fff;border:1px solid var(--line);border-radius:20px;padding:26px 28px 36px;min-height:900px}
.training-posts-content .sidebar-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:30px}
.training-posts-content .sidebar h2{font-size:27px;letter-spacing:1px;margin:0}
.training-posts-content .reset{border:0;background:none;color:#aaaE9f;font-size:16px;padding:0}
.training-posts-content .field{min-width:0;display:block;margin:0 0 34px}
.training-posts-content .field>span{display:block;font-size:19px;letter-spacing:.3px;margin-bottom:10px}
.training-posts-content .select-wrap{position:relative}
.training-posts-content .select-wrap:after{content:"⌄";position:absolute;right:21px;top:12px;color:#64705c;pointer-events:none}
.training-posts-content select{width:100%;height:58px;padding:10px 42px 10px 17px;border:1px solid #dfe3d5;border-radius:12px;background:#fff;appearance:none;font-size:20px}
.training-posts-content .apply{background:var(--yellow);border:0;border-radius:13px;width:100%;height:54px;font-size:21px;letter-spacing:.7px;margin-top:35px}
.training-posts-content .sidebar-note{font-size:13px;line-height:1.8;color:#a4a99a;margin:37px 0 0}
.training-posts-content .search{height:74px;border:1px solid var(--line);background:#fff;border-radius:20px;display:flex;align-items:center;padding:9px 20px 9px 27px;gap:15px}
.training-posts-content .search input{border:0;background:none;outline:none;min-width:0;flex:1;font-size:20px;letter-spacing:.5px}
.training-posts-content .search input::placeholder{color:#aaae9f}
.training-posts-content .search button{background:var(--yellow);border:0;border-radius:14px;width:122px;height:53px;font-size:21px;}
.training-posts-content .results-head{display:flex;align-items:center;justify-content:space-between;margin:29px 0 13px;padding-right:21px}
.training-posts-content .results-head h2{font-size:25px;letter-spacing:.7px;margin:0;}
.training-posts-content .sort{position:relative;margin-right:78px}
.training-posts-content .sort select{width:120px;height:40px;font-size:18px;border:0;background:transparent;color:#9ba08f;padding:0 25px 0 0;text-align:right}
.training-posts-content .sort:after{content:"⌄";position:absolute;right:0;top:5px;font-size:17px;color:#9ba08f;pointer-events:none}
.training-posts-content .chips{display:flex;gap:47px;flex-wrap:wrap;align-items:center;min-height:35px;margin:0 0 27px}
.training-posts-content .chip{background:#fff5d7;color:#b0aa88;border-radius:30px;font-size:16px;padding:4px 16px;line-height:1.6}
.training-posts-content .catalogue-note{font-size:12px;color:#9da590;margin:0 0 15px}
.training-posts-content .catalogue-note:empty{display:none}
.training-posts-content .cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:23px 28px;min-height:548px;align-content:start}
.training-posts-content .card{background:#fff;border:1px solid #e0e3d7;border-radius:20px;padding:20px 23px 22px;min-height:263px;position:relative;display:flex;flex-direction:column}
.training-posts-content .card-top{display:flex;align-items:center;justify-content:space-between;gap:10px}
.training-posts-content .badge{background:var(--pale);color:#8aa27b;border-radius:30px;padding:4px 15px;font-size:16px;line-height:1.6;max-width:85%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.training-posts-content .heart{border:0;background:none;color:#929d87;font-size:29px;line-height:1.2;padding:0 6px}
.training-posts-content .heart[aria-pressed="true"]{color:#a75e45}
.training-posts-content .card h3{font-size:25px;letter-spacing:.1px;line-height:1.5;margin:18px 0 7px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.training-posts-content .provider{color:#9aa08f;font-size:17px;margin:0 0 9px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.training-posts-content .card-meta{font-size:18px;margin:0 0 14px;letter-spacing:.2px}
.training-posts-content .tags{font-size:16px;color:#8ba17d;display:flex;flex-wrap:wrap;gap:10px;padding-right:120px;margin-top:auto}
.training-posts-content .tags span+span:before{content:"/";margin-right:10px;color:#a6b29b}
.training-posts-content .details{position:absolute;right:65px;bottom:25px;color:#a8ae9f;border:0;background:none;font-size:17px;padding:0}
.training-posts-content .details:hover{color:#6a8556}
.training-posts-content .pagination{display:flex;justify-content:center;align-items:center;gap:9px;min-height:49px;margin:70px 0 14px}
.training-posts-content .pagination button{border:1px solid var(--line);border-radius:13px;background:#fff;font-size:19px;min-width:50px;height:48px;padding:4px 16px}
.training-posts-content .pagination .selected{background:var(--yellow);border-color:var(--yellow);}
.training-posts-content .pagination .dots{padding:0 3px;color:var(--muted);font-size:15px}
.training-posts-content footer{display:flex;justify-content:space-between;gap:20px;border-top:1px solid #dfe3d6;padding:20px 0 27px;margin-top:40px;font-size:14px;color:#a2a896;letter-spacing:.4px}
.training-posts-content footer a{color:#8c9780}
.training-posts-content .empty{grid-column:1/-1;min-height:548px;border:1px dashed #d9dfcc;background:#f4f6ed;border-radius:18px;padding:35px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
.training-posts-content .empty h3{font-size:23px;margin:0 0 9px}
.training-posts-content .empty p{color:#8f9b83;font-size:16px;max-width:500px;margin:0 0 18px}
.training-posts-content .empty button{border:1px solid #ccd7bd;background:#fff;border-radius:10px;padding:9px 20px;font-size:16px}
.training-posts-content .loading{opacity:.55;pointer-events:none}
.training-posts-content .error-note{color:#ae7551}
.training-posts-content dialog{border:1px solid #e0e5d7;background:var(--paper);border-radius:21px;box-shadow:0 20px 80px #22351830;width:min(760px,calc(100% - 35px));max-height:88vh;padding:30px;color:var(--ink)}
.training-posts-content dialog::backdrop{background:#1a2c2366;backdrop-filter:blur(3px)}
.training-posts-content .modal-top{display:flex;align-items:center;justify-content:space-between;gap:20px}
.training-posts-content .modal-top p{font-size:12px;letter-spacing:2px;color:#8e9a80;margin:0}
.training-posts-content .close{border:0;background:none;font-size:31px;line-height:1;color:#87977b}
.training-posts-content .modal-title{font-size:26px;line-height:1.5;margin:18px 0 15px}
.training-posts-content .detail-grid{display:grid;grid-template-columns:120px 1fr;gap:12px;font-size:15px;border-top:1px solid var(--line);padding-top:20px}
.training-posts-content .detail-grid dt{color:#8b977d}
.training-posts-content .detail-grid dd{margin:0;overflow-wrap:anywhere}
.training-posts-content .detail-note{padding:14px;border-radius:10px;background:#f5efd7;color:#8a8060;font-size:13px}
.training-posts-content .primary-link{display:block;background:var(--yellow);padding:12px;border-radius:12px;text-align:center;font-size:17px;margin-top:20px}
.training-posts-content .toast{position:fixed;bottom:30px;left:50%;transform:translate(-50%,15px);background:#35482f;color:white;padding:12px 23px;border-radius:11px;font-size:14px;opacity:0;pointer-events:none;transition:.2s;z-index:5;max-width:90vw}
.training-posts-content .toast.show{opacity:1;transform:translate(-50%,0)}
@media(min-width:2100px){.training-posts-content .layout{gap:39px}
.training-posts-content .sidebar{padding:34px 36px 46px;min-height:962px}
.training-posts-content .sidebar h2{font-size:35px}
.training-posts-content .sidebar-head{margin-bottom:39px}
.training-posts-content .reset{font-size:20px}
.training-posts-content .field{margin-bottom:44px}
.training-posts-content .field>span{font-size:24px;margin-bottom:13px}
.training-posts-content select{height:74px;font-size:26px;padding-left:22px}
.training-posts-content .select-wrap:after{top:18px;right:26px}
.training-posts-content .apply{height:69px;font-size:27px;margin-top:45px}
.training-posts-content .sidebar-note{font-size:16px;margin-top:47px}
.training-posts-content .search{height:95px;padding:12px 26px 12px 35px}
.training-posts-content .search input{font-size:26px}
.training-posts-content .search button{width:156px;height:68px;font-size:27px}
.training-posts-content .results-head{margin:37px 0 17px;padding-right:27px}
.training-posts-content .results-head h2{font-size:32px}
.training-posts-content .sort{margin-right:100px}
.training-posts-content .sort select{font-size:23px;width:154px}
.training-posts-content .chips{gap:60px;min-height:45px;margin-bottom:35px}
.training-posts-content .chip{font-size:20px;padding:5px 20px}
.training-posts-content .cards{gap:30px 36px;min-height:702px}
.training-posts-content .card{padding:26px 30px 28px;min-height:337px}
.training-posts-content .badge{font-size:20px;padding:5px 19px}
.training-posts-content .heart{font-size:37px}
.training-posts-content .card h3{font-size:32px;margin-top:23px}
.training-posts-content .provider{font-size:22px}
.training-posts-content .card-meta{font-size:23px;margin-bottom:18px}
.training-posts-content .tags{font-size:20px;padding-right:154px}
.training-posts-content .details{font-size:22px;right:83px;bottom:32px}
.training-posts-content .pagination{margin-top:90px;gap:12px}
.training-posts-content .pagination button{height:62px;min-width:64px;font-size:24px}
.training-posts-content footer{font-size:18px;margin-top:51px;padding:26px 0 35px}}
@media(max-width:1550px){.training-posts-content .layout{gap:25px}
.training-posts-content .sidebar{padding:25px 23px;min-height:690px}
.training-posts-content .sidebar h2{font-size:23px}
.training-posts-content .field>span{font-size:17px}
.training-posts-content select{font-size:17px}
.training-posts-content .card h3{font-size:20px}
.training-posts-content .provider{font-size:14px}
.training-posts-content .card-meta{font-size:15px}
.training-posts-content .badge,.training-posts-content .tags{font-size:13px}
.training-posts-content .details{font-size:14px;right:25px}
.training-posts-content .card{min-height:245px}
.training-posts-content .cards{gap:20px;min-height:510px}
.training-posts-content .sort{margin-right:25px}
.training-posts-content .search input{font-size:17px}
.training-posts-content .chips{gap:22px}}
@media(max-width:1120px){.training-posts-content .layout{gap:20px}
.training-posts-content .sidebar{padding:20px 18px;min-height:650px}
.training-posts-content .sidebar h2{font-size:21px}
.training-posts-content .reset{font-size:13px}
.training-posts-content .field>span{font-size:15px}
.training-posts-content select{font-size:14px;height:50px}
.training-posts-content .apply{font-size:17px}
.training-posts-content .sidebar-note{font-size:11px}
.training-posts-content .cards{gap:15px}
.training-posts-content .card{padding:16px;min-height:260px}
.training-posts-content .card h3{font-size:18px}
.training-posts-content .card-meta{font-size:13px}
.training-posts-content .tags{padding-right:0;margin-bottom:28px;font-size:11px}
.training-posts-content .details{bottom:15px;font-size:12px;right:20px}
.training-posts-content .results-head h2{font-size:20px}
.training-posts-content .chip{font-size:13px}
.training-posts-content .search{padding-left:17px;height:65px}
.training-posts-content .search button{height:45px;width:85px;font-size:17px}
.training-posts-content .search input{font-size:14px}
.training-posts-content .sort{margin-right:0}
.training-posts-content .sort select{font-size:14px}
.training-posts-content .pagination{margin-top:35px}
.training-posts-content footer{font-size:11px}}
@media(max-width:760px){.training-posts-content .layout{display:flex;flex-direction:column;gap:20px}
.training-posts-content .sidebar{width:100%;min-height:0;padding:18px}
.training-posts-content .sidebar-head{margin-bottom:16px}
.training-posts-content .sidebar h2{font-size:20px}
.training-posts-content .filter-form{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.training-posts-content .field{margin:0}
.training-posts-content .field>span{font-size:12px;margin-bottom:5px}
.training-posts-content select{font-size:13px;height:44px;padding-left:12px}
.training-posts-content .select-wrap:after{top:9px;right:14px}
.training-posts-content .apply{margin:0;height:44px;font-size:15px;align-self:end}
.training-posts-content .sidebar-note{margin:12px 0 0;font-size:10px}
.training-posts-content .result-area{width:100%}
.training-posts-content .search{height:58px;border-radius:14px;padding:6px 9px 6px 14px}
.training-posts-content .search input{font-size:13px}
.training-posts-content .search button{height:43px;width:67px;font-size:15px}
.training-posts-content .results-head{margin-top:22px;margin-bottom:9px;padding-right:10px}
.training-posts-content .results-head h2{font-size:19px}
.training-posts-content .chips{gap:9px;margin-bottom:17px;min-height:26px}
.training-posts-content .chip{font-size:11px;padding:3px 10px}
.training-posts-content .cards{grid-template-columns:1fr;min-height:0;gap:14px}
.training-posts-content .card{min-height:240px;padding:18px 20px}
.training-posts-content .card h3{font-size:20px;margin-top:14px}
.training-posts-content .provider{font-size:13px}
.training-posts-content .card-meta{font-size:14px}
.training-posts-content .badge{font-size:12px}
.training-posts-content .tags{font-size:12px;margin-bottom:22px}
.training-posts-content .details{font-size:13px;bottom:17px}
.training-posts-content .pagination{margin-top:25px}
.training-posts-content .pagination button{min-width:38px;height:40px;font-size:15px;padding:4px 10px}
.training-posts-content .empty{min-height:330px;padding:25px}
.training-posts-content .empty h3{font-size:19px}
.training-posts-content .empty p{font-size:13px}
.training-posts-content footer{flex-direction:column;gap:5px;font-size:10px;margin-top:30px}
.training-posts-content .detail-grid{grid-template-columns:85px 1fr;font-size:12px;gap:10px}
.training-posts-content .modal-title{font-size:21px}}
@media(prefers-reduced-motion:reduce){.training-posts-content *{transition:none!important}}
</style>
<style>__CC_CSS__</style>
</head>
<body class="cc-member-page cc-training-page">
__CC_HEADER____CC_MENU__
<div class="training-posts-content" data-member-content>
<main class="cc-page">
<section class="cc-page-heading"><p class="eyebrow">YOUR NEXT DIRECTION</p><h1>다음 성장을 위한 교육을 찾아보세요</h1><p class="subtitle">직무에 필요한 교육을 조건별로 살펴보고 관심목록에 저장하세요.</p></section>
<div class="layout">
<section class="result-area" aria-label="교육 검색 결과">
<form class="search" id="searchForm"><input id="searchInput" type="search" aria-label="교육 검색" placeholder="교육명, 교육기관 또는 기술 검색" maxlength="200"><button type="submit" id="searchButton">검색</button></form>
<div class="results-head"><h2 id="resultsTitle" aria-live="polite">검색된 교육</h2><a class="cc-top-button cc-main-button ai-recommend-link" href="/training_match">AI 교육 추천 받기</a></div>
<div id="chips" class="chips" aria-label="적용된 검색 조건"></div>
<p id="dataNote" class="catalogue-note" role="status"></p>
<div id="cards" class="cards" aria-live="polite"></div>
<nav id="pagination" class="pagination" aria-label="교육 페이지"></nav>
</section>
</div>
<footer><span>취준나침반 · 한 번에 찾고, 한 걸음씩 준비해요.</span><span id="sourceNote">교육모음 · 고용24 실제 교육 정보</span></footer>
</main>
<dialog id="detailDialog" aria-labelledby="detailTitle"><div class="modal-top"><p>COURSE DETAILS</p><button class="close" type="button" id="closeDetail" aria-label="교육 상세 닫기">×</button></div><div id="detailBody"></div></dialog>
<div class="toast" id="toast" role="status"></div>
<script id="initial-data" type="application/json">__INITIAL_DATA__</script>
<script>
"use strict";
const el = (id) => document.getElementById(id);
const PAGE_SIZE = 4;
const state = {data:JSON.parse(el("initial-data").textContent),filtered:[],page:0,saved:[],filter:{category:"",mode:"all",budget:"",query:""},controller:null,generation:0};
const courseBookmarks = CompassBookmarks.create("course");
const esc=(value)=>String(value??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const modeName=(value)=>({online:"온라인",offline:"오프라인",mixed:"혼합",unknown:"방식 확인 필요",all:"전체 방식"}[value]||"방식 확인 필요");
const costText=(value)=>value==null?"교육비 원문 확인":value===0?"무료":value.toLocaleString("ko-KR")+"원";
const safeUrl=(value)=>{try{const u=new URL(value);return ["https:","http:"].includes(u.protocol)&&["www.work24.go.kr","work24.go.kr","hrd.work24.go.kr","www.hrd.go.kr"].includes(u.hostname)?u.href:"";}catch{return "";}};
let toastTimer;
function toast(message){el("toast").textContent=message;el("toast").classList.add("show");clearTimeout(toastTimer);toastTimer=setTimeout(()=>el("toast").classList.remove("show"),2800);}
function pendingFilter(){return {query:el("searchInput").value.trim()};}
function applyFilters(){
  const f=state.filter;
  state.filtered=state.data.courses.filter(c=>{
    if(f.query){const haystack=[c.title,c.provider,c.categoryName,...c.tags].join(" ").toLocaleLowerCase();const terms=f.query.toLocaleLowerCase().split(/\s+/).filter(Boolean);if(!terms.every(t=>haystack.includes(t)))return false;}
    return true;
  });
  state.filtered.sort((a,b)=>b.start.localeCompare(a.start)||a.key.localeCompare(b.key));
  state.page=0;render();
}
function render(){
  const total=state.filtered.length;
  const pages=Math.ceil(total/PAGE_SIZE);
  state.page=Math.max(0,Math.min(state.page,Math.max(0,pages-1)));
  el("resultsTitle").textContent="검색된 교육 "+total+"개";
  const f=state.filter,chips=[];
  if(f.query)chips.push("검색: "+f.query);
  el("chips").innerHTML=chips.map(text=>'<span class="chip">'+esc(text)+'</span>').join("");
  el("dataNote").textContent=state.data.errors.length?state.data.errors.map(item=>item.message).join(" "):"";
  el("dataNote").classList.toggle("error-note",state.data.errors.length>0);
  el("sourceNote").textContent="고용24 · Supabase 저장 자료 · "+state.data.fetchedAt+" 조회";
  const visible=state.filtered.slice(state.page*PAGE_SIZE,(state.page+1)*PAGE_SIZE);
  el("cards").innerHTML=visible.length?visible.map(c=>{
    const saved=state.saved.includes(c.key);
    const tags=c.tags.length?c.tags:[c.categoryName];
    return '<article class="card"><div class="card-top"><span class="badge">'+esc(c.badge)+'</span><button class="heart" type="button" data-save="'+esc(c.key)+'" aria-label="'+esc(c.title)+' 관심 '+(saved?'해제':'저장')+'" aria-pressed="'+saved+'"'+(!courseBookmarks.ready||courseBookmarks.isPending(c.key)?' disabled':'')+'>'+ (saved?'♥':'♡')+'</button></div><h3 title="'+esc(c.title)+'">'+esc(c.title)+'</h3><p class="provider">'+esc(c.provider)+'</p><p class="card-meta">'+esc(costText(c.cost))+' · '+esc(modeName(c.mode))+' · '+(c.weeks?c.weeks+'주':'기간 확인')+'</p><div class="tags">'+tags.map(t=>'<span>'+esc(t)+'</span>').join("")+'</div><button class="details" type="button" data-detail="'+esc(c.key)+'">상세 보기 →</button></article>';
  }).join(""):'<div class="empty"><h3>조건에 맞는 교육이 없어요</h3><p>검색어나 분야·교육 방식·교육비 조건을 넓혀서 다시 찾아보세요. 금액이 확인되지 않은 교육은 교육비 제한에서 제외됩니다.</p><button id="emptyReset" type="button">조건 초기화</button></div>';
  el("emptyReset")?.addEventListener("click",reset);
  if(pages<=1){el("pagination").innerHTML="";return;}
  const indexes=new Set([0,pages-1]);
  for(let p=Math.max(0,state.page-1);p<=Math.min(pages-1,state.page+2);p++)indexes.add(p);
  let html="",previous=-1;
  if(state.page>0)html+='<button type="button" data-page="'+(state.page-1)+'" aria-label="이전 페이지">이전</button>';
  for(const p of [...indexes].sort((a,b)=>a-b)){
    if(previous>=0&&p-previous>1)html+='<span class="dots">…</span>';
    html+='<button type="button" data-page="'+p+'" class="'+(p===state.page?'selected':'')+'" '+(p===state.page?'aria-current="page"':'')+' aria-label="'+(p+1)+'페이지">'+(p+1)+'</button>';
    previous=p;
  }
  if(state.page<pages-1)html+='<button type="button" data-page="'+(state.page+1)+'" aria-label="다음 페이지">다음</button>';
  el("pagination").innerHTML=html;
}
async function reloadAndApply(){
  state.controller?.abort();state.controller=new AbortController();
  const generation=++state.generation,nextFilter=pendingFilter();
  el("cards").classList.add("loading");el("cards").setAttribute("aria-busy","true");
  el("searchButton").disabled=true;el("dataNote").textContent="저장된 교육목록을 불러오고 있어요…";
  try{
    const response=await fetch("/training_posts?data=1",{signal:state.controller.signal,cache:"no-store"});
    if(!response.ok)throw new Error("조회 실패");
    const data=await response.json();
    if(generation!==state.generation)return;
    state.data=data;state.filter=nextFilter;applyFilters();
  }catch(error){
    if(error.name==="AbortError"||generation!==state.generation)return;
    el("dataNote").textContent="새 조회에 실패했습니다. 현재 화면을 유지하며, 검색으로 다시 시도할 수 있어요.";el("dataNote").classList.add("error-note");
  }finally{
    if(generation===state.generation){el("cards").classList.remove("loading");el("cards").setAttribute("aria-busy","false");el("searchButton").disabled=false;}
  }
}
function reset(){el("searchInput").value="";reloadAndApply();}
function showDetails(c){
  const url=safeUrl(c.url);
  const fields=[["교육기관",c.provider],["분야",c.categoryName],["교육 방식",modeName(c.mode)+(c.modeEvidence?" · "+c.modeEvidence:"")],["교육 기간",(c.start||"미정")+" ~ "+(c.end||"미정")],["API 수강비",costText(c.cost)],["실제 훈련비",c.rawRealCost?c.rawRealCost+"원":"원문 확인"],["개인 본인부담금","고용24 원문에서 확인"],["지역",c.address||"원문 확인"],["과정 ID",c.courseId],["훈련 회차",c.round?c.round+"회차":"미제공"],["NCS 코드",c.ncsCode||"미제공"]];
  el("detailBody").innerHTML='<h2 class="modal-title" id="detailTitle">'+esc(c.title)+'</h2><dl class="detail-grid">'+fields.map(([label,value])=>'<dt>'+esc(label)+'</dt><dd>'+esc(value)+'</dd>').join("")+'</dl><p class="detail-note">저장된 교육명·기관·주소·기간을 표시합니다. 분야·교육 방식·교육비·회차는 제공되지 않아 원문 확인이 필요합니다.</p>'+(url?'<a class="primary-link" href="'+esc(url)+'" target="_blank" rel="noopener noreferrer">고용24 원문 보기 ↗</a>':'');
  el("detailDialog").showModal();
}
el("searchForm").addEventListener("submit",e=>{e.preventDefault();reloadAndApply();});
el("resetButton").addEventListener("click",reset);
el("sort").addEventListener("change",applyFilters);
el("cards").addEventListener("click",async e=>{
  const save=e.target.closest("[data-save]"),detail=e.target.closest("[data-detail]");
  if(save){
    const key=save.dataset.save;
    if(!courseBookmarks.ready||courseBookmarks.isPending(key))return;
    const operation=courseBookmarks.toggle(key);render();
    try{
      const saved=await operation;
      state.saved=courseBookmarks.ids();
      toast(saved?"관심목록에 저장했어요.":"관심목록에서 해제했어요.");
    }catch(error){toast(error.message);if(error.loginRequired)location.assign("/signin");}
    finally{render();}
  }
  if(detail){const c=state.data.courses.find(c=>c.key===detail.dataset.detail);if(c)showDetails(c);}
});
el("pagination").addEventListener("click",e=>{const button=e.target.closest("[data-page]");if(button){state.page=Number(button.dataset.page);render();}});
el("closeDetail").addEventListener("click",()=>el("detailDialog").close());
el("detailDialog").addEventListener("click",e=>{if(e.target===el("detailDialog")){const box=e.target.getBoundingClientRect();if(e.clientX<box.left||e.clientX>box.right||e.clientY<box.top||e.clientY>box.bottom)e.target.close();}});
const initialQuery = (new URLSearchParams(location.search).get("q") || "").slice(0,200);
el("searchInput").value = initialQuery;
state.filter.query = initialQuery;
applyFilters();
courseBookmarks.load().then(()=>{state.saved=courseBookmarks.ids();render();}).catch(error=>toast(error.message));
window.addEventListener("pageshow",event=>{if(event.persisted)courseBookmarks.load().then(()=>{state.saved=courseBookmarks.ids();render();}).catch(error=>{render();toast(error.message);});});
</script>
</div>
__CC_SCRIPT__
</body></html>
"""
