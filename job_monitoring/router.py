"""채용공고 모니터링 설정 화면."""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from modules.auth import auth_store
from shared.components.compass import apply_member_shell

router = APIRouter(tags=["채용공고 모니터링"])


@router.get("/job_mointoring", response_class=HTMLResponse, summary="채용공고 모니터링 설정")
def monitoring_page(request: Request):
    try:
        user = auth_store.me(request)
    except HTTPException as exc:
        if exc.status_code == 401:
            return RedirectResponse("/signin", status_code=303)
        raise

    page = """<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>채용공고 모니터링 설정 · 취준나침반</title><style>__CC_CSS__
html,body{max-width:100%;overflow-x:hidden}.cc-page{width:100%;max-width:100%;box-sizing:border-box;overflow-x:hidden}.monitoring-toolbar{display:flex;justify-content:space-between;align-items:center;gap:20px;margin:0 0 27px}.monitoring-heading .eyebrow{margin:0 0 10px}.monitoring-heading .page-title{margin:0 0 6px}.monitoring-heading .page-subtitle{margin:0}.monitoring-controls{display:flex;flex-shrink:0;gap:8px}.monitoring-controls button{padding:8px 12px;border:1px solid var(--cc-border);border-radius:7px;background:white;color:var(--cc-text);font:inherit;cursor:pointer}.monitoring-controls .primary{background:var(--cc-yellow);border-color:var(--cc-yellow)}.monitoring-panel{width:100%;max-width:100%;min-width:0;box-sizing:border-box;padding:20px;background:white;border:0;border-radius:14px;overflow:hidden}.monitoring-table{width:100%;max-width:100%;min-width:0}.monitoring-row{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.35fr) minmax(0,1.35fr);align-items:center;gap:10px;padding:9px 0;border-bottom:1px solid var(--cc-border)}.monitoring-row:last-child{border-bottom:0}.monitoring-head{color:var(--cc-muted);font-size:11px;border-bottom:1px solid var(--cc-border)}.monitoring-head span:last-child{display:none}.monitoring-row input{display:block;width:100%;min-width:0;max-width:100%;box-sizing:border-box;height:34px;border:1px solid var(--cc-border);border-radius:6px;padding:0 9px;color:var(--cc-text);font:inherit}.monitoring-row button{display:none}@media(max-width:760px){.monitoring-toolbar{align-items:flex-start;flex-direction:column;gap:12px;margin-bottom:20px}.monitoring-controls{width:100%}.monitoring-panel{padding:16px 0}.monitoring-head{display:none}.monitoring-row{grid-template-columns:1fr;gap:7px;padding:10px 0}.monitoring-row input{height:36px}}
</style></head><body class="cc-member-page" data-page="mypage">__CC_HEADER__ __CC_MENU__<main class="cc-page" data-member-content><div class="monitoring-toolbar"><section class="monitoring-heading"><p class="eyebrow">SETTINGS</p><h1 class="page-title">채용공고 모니터링 설정</h1><p class="page-subtitle">플랫폼별 채용공고 알림 이메일 연결을 관리해요.</p></section><div class="monitoring-controls"><button id="add-row" type="button">+ 플랫폼 추가</button><button class="primary" type="button">저장</button></div></div><section class="monitoring-panel"><div class="monitoring-table"><div class="monitoring-row monitoring-head"><span>플랫폼명</span><span>발신 이메일 주소</span><span>수신 이메일 주소</span><span>작업</span></div><div id="monitoring-rows"><div class="monitoring-row"><input type="text" aria-label="플랫폼명" placeholder="잡코리아"><input type="email" aria-label="발신 이메일 주소" placeholder="job-alert@example.com"><input type="email" aria-label="수신 이메일 주소" placeholder="me@example.com"><button type="button" hidden>삭제</button></div></div></div></section></main><script>const list=document.getElementById('monitoring-rows'),add=document.getElementById('add-row');add.addEventListener('click',()=>{const row=document.createElement('div');row.className='monitoring-row';row.innerHTML='<input type="text" aria-label="플랫폼명" placeholder="사람인"><input type="email" aria-label="발신 이메일 주소" placeholder="job-alert@example.com"><input type="email" aria-label="수신 이메일 주소" placeholder="me@example.com"><button type="button">삭제</button>';list.append(row);});</script>__CC_SCRIPT__</body></html>"""
    return HTMLResponse(apply_member_shell(page, user, "mypage"))
