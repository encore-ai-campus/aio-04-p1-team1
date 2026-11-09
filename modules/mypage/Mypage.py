"""마이페이지 라우터. app.py에서 회원 인증·관심 정보 API와 함께 실행합니다."""

from html import escape

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from modules.auth import auth_store
from modules.main.member_shell import apply_member_shell
from modules.mypage.bookmarks_ui import CONTENT as BOOKMARKS_CONTENT, SCRIPT as BOOKMARKS_SCRIPT

router = APIRouter(tags=["마이페이지"])

def page_user(request):
    try:
        return auth_store.me(request)
    except HTTPException as exc:
        if exc.status_code == 401:
            return RedirectResponse("/signin", status_code=303)
        raise


def render_member_page(page, user):
    if page == "main":
        from modules.main.page import render_main
        return render_main(user)
    if page == "home":
        from modules.mypage.dashboard_ui import render_dashboard
        return render_dashboard(user)
    titles = {"main": ("우리의 다음 걸음이 시작되는 곳", "메인 화면 연결 확인"),
              "home": ("나의 취업 준비를 한곳에서", "마이페이지"),
              "bookmarks": ("다시 보고 싶은 기회를 모았어요", "관심목록"),
              "profile": ("나를 소개하는 기본 정보", "내 정보")}
    subtitle, title = titles[page]
    if page == "profile":
        content = '''<section class="panel profile"><h2>기본 정보</h2><p class="muted">계정에 등록된 정보를 확인하고 이름을 수정할 수 있어요.</p><form id="profile-form"><label for="profile-name">이름</label><input id="profile-name" name="name" minlength="2" maxlength="30" value="__NAME__" required><label for="profile-email">이메일</label><input id="profile-email" type="email" value="__EMAIL__" readonly><p class="hint">가입 이메일은 이 화면에서 변경할 수 없어요.</p><div class="profile-button-bar"><div class="password-change-row"><button class="button" id="password-change-open" type="button">비밀번호 변경</button></div><div class="profile-actions"><button class="button withdraw-trigger" id="withdraw-open" type="button">탈퇴하기</button><button class="button primary" id="profile-save" type="submit">변경 내용 저장</button></div></div></form><p id="profile-message" role="status" aria-live="polite"></p></section>

<dialog class="password-dialog" id="password-dialog" aria-labelledby="password-dialog-title" aria-describedby="password-dialog-note">
<h2 id="password-dialog-title">비밀번호 변경</h2><p id="password-dialog-note">이전 비밀번호를 확인한 뒤 새 비밀번호로 변경합니다. 변경 후에는 다시 로그인해 주세요.</p>
<form id="password-change-form"><label for="password-current">이전 비밀번호</label><input id="password-current" name="current_password" type="password" autocomplete="current-password" maxlength="128" required autofocus>
<label for="password-new">새 비밀번호</label><input id="password-new" name="new_password" type="password" autocomplete="new-password" minlength="8" maxlength="128" required aria-describedby="password-strength-note"><p class="password-help" id="password-strength-note">영문과 숫자를 포함해 8~128자로 입력해 주세요.</p>
<label for="password-confirm">새 비밀번호 확인</label><input id="password-confirm" name="password_confirm" type="password" autocomplete="new-password" minlength="8" maxlength="128" required>
<p id="password-change-message" class="password-change-message" role="status" aria-live="polite" tabindex="-1"></p><div class="password-dialog-actions"><button class="button" id="password-change-cancel" type="button">취소</button><button class="button primary" id="password-change-submit" type="submit">비밀번호 변경</button></div></form></dialog>
<dialog class="withdraw-dialog" id="withdraw-dialog" aria-labelledby="withdraw-title" aria-describedby="withdraw-note">
<div class="withdraw-icon" aria-hidden="true">!</div><h2 id="withdraw-title">회원 탈퇴</h2>
<p class="withdraw-intro">보안을 위해 현재 사용 중인 비밀번호를 확인해 주세요.</p>
<p class="withdraw-note" id="withdraw-note"><strong>탈퇴 기능 준비 중</strong><br>현재는 비밀번호 확인만 가능하며, 계정과 데이터는 삭제되지 않습니다.</p>
<form id="withdraw-form"><label for="withdraw-password">비밀번호</label><input id="withdraw-password" name="password" type="password" autocomplete="current-password" maxlength="128" required autofocus>
<label for="withdraw-password-confirm">비밀번호 확인</label><input id="withdraw-password-confirm" name="password_confirm" type="password" autocomplete="current-password" maxlength="128" required>
<p class="withdraw-message" id="withdraw-message" role="status" aria-live="polite" tabindex="-1"></p>
<div class="withdraw-actions"><button class="button" id="withdraw-cancel" type="button">취소</button><button class="button withdraw-trigger" id="withdraw-submit" type="submit">탈퇴하기</button></div>
</form></dialog>'''
    else:
        content = BOOKMARKS_CONTENT
    html = TEMPLATE.replace("__CONTENT__", content).replace("__PAGE__", page)
    html = html.replace("__BOOKMARKS_SCRIPT__", BOOKMARKS_SCRIPT if page == "bookmarks" else "")
    html = html.replace("__TITLE__", title).replace("__SUBTITLE__", subtitle)
    html = html.replace("__NAME__", escape(user["name"], quote=True)).replace("__EMAIL__", escape(user["email"], quote=True))
    return HTMLResponse(apply_member_shell(html, user, 'mypage'))


@router.get("/mypage", response_class=HTMLResponse, summary="마이페이지 홈")
def mypage(request: Request):
    user = page_user(request)
    return user if isinstance(user, RedirectResponse) else render_member_page("home", user)


@router.get("/mypage/bookmarks", response_class=HTMLResponse, summary="관심목록 페이지")
def bookmarks_page(request: Request):
    user = page_user(request)
    return user if isinstance(user, RedirectResponse) else RedirectResponse("/mypage#bookmarks", status_code=303)


@router.get("/mypage/profile", response_class=HTMLResponse, summary="내 정보 페이지")
def profile_page(request: Request):
    user = page_user(request)
    return user if isinstance(user, RedirectResponse) else render_member_page("profile", user)


TEMPLATE = r'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__ · 취준나침반</title>
<style>
:root{--ink:#263127;--muted:#777d70;--yellow:#f7ca43;--cream:#faf9f5;--line:#e4e6dd}*{box-sizing:border-box}body{margin:0;background:var(--cream);color:var(--ink);font-family:"Malgun Gothic","Apple SD Gothic Neo",sans-serif}a{color:inherit;text-decoration:none}button,input{font:inherit}button,a,input{ -webkit-tap-highlight-color:transparent}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #93823c;outline-offset:3px}button{cursor:pointer}button:disabled{opacity:.5;cursor:default}.hidden{display:none!important}.sr-only{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}
header{border-bottom:1px solid var(--line);background:white}.header-inner{max-width:1180px;margin:auto;min-height:80px;padding:15px 30px;display:flex;align-items:center;justify-content:space-between;gap:20px}.brand{font-size:20px;font-weight:800;display:flex;align-items:center;gap:10px;letter-spacing:-1px}.brand-icon{width:32px;height:32px;background:var(--yellow);border:1px solid var(--ink);border-radius:50%;display:grid;place-items:center;font-size:22px}.nav{display:flex;gap:22px;align-items:center;font-size:12px}.nav a:hover{text-decoration:underline;text-underline-offset:5px}.logout{background:none;border:0;color:var(--muted);font-size:12px;padding:8px 0}
.layout{max-width:1120px;margin:44px auto 60px;padding:0 24px;display:grid;grid-template-columns:200px 1fr;gap:38px}.sidebar{padding-top:4px}.user-label{font-size:11px;color:var(--muted);margin-bottom:8px}.user-name{font-size:22px;font-weight:800;margin-bottom:28px;overflow-wrap:anywhere}.side-nav{display:grid;gap:6px}.side-nav a{padding:13px 15px;border-radius:10px;color:#737968;font-size:13px}.side-nav a.active{background:#f8e8a6;color:var(--ink);font-weight:700}.side-nav a:hover{background:#f4f0df}.side-note{border-top:1px solid var(--line);margin-top:26px;padding-top:20px;font-size:11px;color:var(--muted);line-height:1.8}.eyebrow{font-size:10px;color:#8a8d7b;letter-spacing:2px;font-weight:700;margin:0 0 9px}.page-title{font-size:29px;letter-spacing:-1.2px;margin:0 0 10px}.page-subtitle{font-size:13px;color:var(--muted);margin:0 0 27px}.panel{padding:28px;background:white;border:1px solid var(--line);border-radius:18px}.panel h2{font-size:21px;line-height:1.6;margin:16px 0 10px;letter-spacing:-.7px}.panel p{font-size:13px;line-height:1.9}.welcome{background:#f7f0d2}.badge{font-size:10px;display:inline-block;padding:6px 10px;background:#fff9e5;border:1px solid #e9ddb0;border-radius:20px;color:#7f7449;letter-spacing:.4px}.menu-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:20px}.menu-card{background:white;border:1px solid var(--line);border-radius:18px;padding:25px;transition:transform .2s,border-color .2s}.menu-card:hover{transform:translateY(-3px);border-color:#ccba6f}.tile-icon{display:grid;place-items:center;width:40px;height:40px;background:#fcf5d9;border-radius:12px;font-size:25px;margin-bottom:21px}.card-label{font-size:18px;font-weight:800}.menu-card p{font-size:12px;color:var(--muted);line-height:1.9}.card-foot{font-size:12px;display:block;margin-top:25px}.button{display:inline-flex;align-items:center;justify-content:center;gap:7px;padding:11px 16px;background:white;color:var(--ink);border:1px solid var(--line);border-radius:9px;font-size:12px;white-space:nowrap}.button.primary{background:var(--yellow);border-color:var(--yellow);font-weight:700}.button:hover{border-color:#bcab63}.placeholder{padding:36px}.placeholder .button{margin-top:12px}.muted{color:var(--muted)}.profile{max-width:590px}.profile h2{margin-top:0}.profile form{margin-top:26px}.profile label{display:block;font-size:12px;font-weight:700;margin:20px 0 9px}input{height:45px;border:1px solid #dfe2d8;border-radius:9px;padding:0 13px;font-size:12px;min-width:0;color:var(--ink);background:white}.profile input{width:100%}input[readonly]{background:#f7f8f3;color:#7f8576}.hint{font-size:11px!important;color:var(--muted)}.profile .button{margin-top:18px}.error{color:#aa382a!important}.success{color:#426032!important}.list-tools{display:flex;flex-wrap:wrap;gap:20px;justify-content:space-between;align-items:center}.filters{display:flex;gap:5px;flex-wrap:wrap}.filter{padding:10px 12px;background:white;border:1px solid transparent;border-radius:8px;font-size:12px;color:var(--muted)}.filter.active{background:#fff2c4;color:var(--ink);border-color:#f1df9c}.filter span{margin-left:4px;font-size:11px}.search{display:flex;gap:8px;width:100%;margin-top:3px}.search input{flex:1}.bookmark-list{display:grid;gap:14px;margin-top:20px}.bookmark-card{border:1px solid var(--line);border-radius:13px;padding:21px}.bookmark-card h2{font-size:16px;margin:12px 0 6px;overflow-wrap:anywhere}.bookmark-card p{font-size:12px;margin:6px 0;color:var(--muted)}.card-actions{display:flex;gap:8px;justify-content:flex-end;margin-top:16px}.remove{color:#8f5946}.empty{text-align:center;padding:48px 12px}.empty>span{display:block;font-size:38px;color:#bca76a}.empty h2{font-size:19px}.empty p{color:var(--muted);font-size:12px}.empty .button{margin-top:12px}.pagination{display:flex;align-items:center;justify-content:center;gap:16px;margin-top:24px;font-size:12px}.flash{min-height:18px;font-size:12px;color:#8d543e;line-height:1.7;margin-top:18px}footer{padding:20px;text-align:center;font-size:10px;color:#999e91}
@media(max-width:760px){.header-inner{padding:15px 20px;gap:10px}.brand{font-size:17px}.nav{gap:12px;font-size:11px}.nav .username{display:none}.layout{display:block;margin-top:24px;padding:0 16px}.sidebar{margin-bottom:28px}.user-label,.user-name,.side-note{display:none}.side-nav{display:flex;gap:6px;flex-wrap:wrap}.side-nav a{padding:10px 13px;font-size:12px}.page-title{font-size:26px}.page-subtitle{font-size:12px;line-height:1.8}.panel{padding:21px}.menu-grid{grid-template-columns:1fr}.menu-card{padding:22px}.tile-icon{margin-bottom:14px}.card-foot{margin-top:16px}.filters{gap:0}.filter{padding:10px}.card-actions{justify-content:flex-start;flex-wrap:wrap}}

.profile-actions{display:flex;align-items:center;justify-content:flex-end;gap:10px;flex-wrap:wrap;margin-top:18px}.profile .profile-actions .button{margin-top:0}.button.withdraw-trigger{background:#c8463c;border-color:#c8463c;color:white;font-weight:700}.button.withdraw-trigger:hover{background:#b63b32;border-color:#b63b32}
.withdraw-dialog{width:calc(100% - 32px);max-width:460px;max-height:88vh;overflow:auto;border:1px solid var(--line);border-radius:20px;padding:29px;color:var(--ink);box-shadow:0 18px 70px #26312725}.withdraw-dialog::backdrop{background:#26312766}.withdraw-icon{display:grid;place-items:center;width:42px;height:42px;border-radius:50%;background:#fff0ed;color:#b63b32;font-size:23px;font-weight:800;margin-bottom:14px}.withdraw-dialog h2{font-size:23px;margin:0 0 10px;letter-spacing:-.7px}.withdraw-intro{font-size:12px;line-height:1.9;color:var(--muted);margin:0 0 16px}.withdraw-note{font-size:12px;line-height:1.9;background:#fff6ef;color:#8b6249;border:1px solid #f0dfd3;border-radius:10px;padding:12px 14px;margin:0 0 21px}.withdraw-dialog label{display:block;font-size:12px;font-weight:700;margin:16px 0 8px}.withdraw-dialog input{width:100%;font-size:14px}.withdraw-message{font-size:12px;line-height:1.9;min-height:20px;margin:14px 0;outline:none}.withdraw-actions{display:flex;justify-content:flex-end;gap:9px}.withdraw-actions .button{margin:0;min-width:76px}.withdraw-dialog button:disabled{cursor:wait}.withdraw-message:focus-visible{outline:2px solid #bcb48b;outline-offset:4px}

.profile-button-bar{display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;margin-top:18px}.profile-button-bar .password-change-row,.profile-button-bar .profile-actions{margin-top:0}.profile-button-bar .profile-actions{margin-left:auto}.password-change-row{display:flex;justify-content:flex-start;margin-top:16px}.profile .password-change-row .button{margin:0}.password-dialog{width:calc(100% - 32px);max-width:460px;max-height:88vh;overflow:auto;border:1px solid var(--line);border-radius:20px;padding:29px;color:var(--ink);box-shadow:0 18px 70px #26312725}.password-dialog::backdrop{background:#26312766}.password-dialog h2{font-size:23px;margin:0 0 10px;letter-spacing:-.7px}.password-dialog>p{font-size:12px;line-height:1.9;color:var(--muted);margin:0 0 20px}.password-dialog label{display:block;font-size:12px;font-weight:700;margin:16px 0 8px}.password-dialog input{width:100%;font-size:14px}.password-dialog .password-help{font-size:10px;line-height:1.8;color:var(--muted);margin:7px 0 0}.password-change-message{font-size:12px;line-height:1.9;min-height:20px;margin:14px 0;outline:none}.password-dialog-actions{display:flex;justify-content:flex-end;gap:9px}.password-dialog-actions .button{margin:0;min-width:76px}

__CC_CSS__
</style></head><body class="cc-member-page" data-page="__PAGE__">__CC_HEADER__
__CC_MENU__
<div class="cc-page" data-member-content><section class="cc-page-heading"><p class="eyebrow">YOUR NEXT DIRECTION</p><h1 class="page-title">__TITLE__</h1><p class="page-subtitle">__SUBTITLE__</p></section><div class="layout cc-account-grid"><aside class="sidebar"><div class="user-label">MY COMPASS</div><div class="user-name">__NAME__님</div><nav class="side-nav" aria-label="마이페이지 메뉴"><a href="/mypage" data-menu="home">마이페이지 홈</a><a href="/mypage#bookmarks" data-menu="bookmarks">관심목록</a></nav><p class="side-note">각자의 속도로,<br>더 선명한 내일을 향해.</p></aside><main>__CONTENT__<p id="flash" class="flash" role="status" aria-live="polite"></p></main></div></div><footer>© 2026 취준나침반 · 한 번에 찾고, 한 걸음씩 준비해요.</footer>
<script>
const page=document.body.dataset.page;
const selected=document.querySelector(`[data-menu="${page}"]`);if(selected){selected.classList.add('active');selected.setAttribute('aria-current','page');}
async function api(url,options={}){const response=await fetch(url,options);if(response.status===401){location.assign('/signin');throw new Error('로그인이 필요합니다.');}if(response.status===204)return null;const data=await response.json();if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:data.error?.message||'요청을 처리하지 못했습니다.');return data;}

if(page==='home'){api('/api/bookmarks?size=1').then(data=>document.getElementById('saved-count').textContent=`저장한 정보 ${data.counts.all}개 →`).catch(error=>document.getElementById('flash').textContent=error.message);}
if(page==='profile'){document.getElementById('profile-form').addEventListener('submit',async event=>{event.preventDefault();const button=document.getElementById('profile-save'),message=document.getElementById('profile-message');button.disabled=true;message.textContent='저장 중…';try{const data=await api('/api/auth/me',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:document.getElementById('profile-name').value})});document.querySelectorAll('.user-name,.username').forEach(node=>node.textContent=data.name+'님');message.className='success';message.textContent='변경 내용을 저장했습니다.';}catch(error){message.className='error';message.textContent=error.message;}finally{button.disabled=false;}});}

if(page==='profile'){
 const dialog=document.getElementById('withdraw-dialog'),form=document.getElementById('withdraw-form'),open=document.getElementById('withdraw-open'),cancel=document.getElementById('withdraw-cancel'),submit=document.getElementById('withdraw-submit'),message=document.getElementById('withdraw-message');
 open.addEventListener('click',()=>{form.reset();message.textContent='';message.className='withdraw-message';dialog.showModal();});
 cancel.addEventListener('click',()=>dialog.close());
 dialog.addEventListener('cancel',event=>{if(submit.disabled)event.preventDefault();});
 dialog.addEventListener('close',()=>{form.reset();message.textContent='';open.focus();});
 form.addEventListener('submit',async event=>{
  event.preventDefault();if(submit.disabled)return;
  const password=document.getElementById('withdraw-password').value,confirmation=document.getElementById('withdraw-password-confirm').value;
  message.className='withdraw-message';message.textContent='';
  if(password!==confirmation){message.className='withdraw-message error';message.textContent='비밀번호 확인이 일치하지 않습니다.';document.getElementById('withdraw-password-confirm').focus();return;}
  submit.disabled=true;cancel.disabled=true;submit.textContent='확인 중…';message.textContent='비밀번호를 확인하고 있어요.';
  try{const data=await api('/api/auth/withdrawal',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password,password_confirm:confirmation})});form.reset();if(data.withdrawal_completed){location.replace('/signin');return;}message.className='withdraw-message success';message.textContent=data.message;message.focus();}
  catch(error){form.reset();message.className='withdraw-message error';message.textContent=error.message;message.focus();}
  finally{submit.disabled=false;cancel.disabled=false;submit.textContent='탈퇴하기';}
 });
}


if(page==='profile'){
 const dialog=document.getElementById('password-dialog'),form=document.getElementById('password-change-form'),open=document.getElementById('password-change-open'),cancel=document.getElementById('password-change-cancel'),submit=document.getElementById('password-change-submit'),message=document.getElementById('password-change-message');let changed=false;
 open.addEventListener('click',()=>{changed=false;form.reset();form.querySelectorAll('input').forEach(node=>node.disabled=false);cancel.textContent='취소';submit.textContent='비밀번호 변경';message.textContent='';message.className='password-change-message';dialog.showModal();});
 cancel.addEventListener('click',()=>dialog.close());dialog.addEventListener('cancel',event=>{if(submit.disabled)event.preventDefault();});
 dialog.addEventListener('close',()=>{form.reset();if(changed){location.replace('/signin');return;}open.focus();});
 form.addEventListener('submit',async event=>{event.preventDefault();if(submit.disabled)return;if(changed){location.replace('/signin');return;}const previous=document.getElementById('password-current'),next=document.getElementById('password-new'),confirm=document.getElementById('password-confirm');message.className='password-change-message';message.textContent='';
  if(next.value!==confirm.value){message.className='password-change-message error';message.textContent='새 비밀번호 확인이 일치하지 않습니다.';confirm.focus();return;}
  if(!/[A-Za-z]/.test(next.value)||!/[0-9]/.test(next.value)){message.className='password-change-message error';message.textContent='새 비밀번호는 영문과 숫자를 모두 포함해 주세요.';next.focus();return;}
  if(previous.value===next.value){message.className='password-change-message error';message.textContent='새 비밀번호는 이전 비밀번호와 다르게 입력해 주세요.';next.focus();return;}
  submit.disabled=true;cancel.disabled=true;submit.textContent='변경 중…';message.textContent='비밀번호를 확인하고 변경하고 있어요.';
  try{const data=await api('/api/auth/password',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({current_password:previous.value,new_password:next.value,password_confirm:confirm.value})});form.reset();changed=data.password_changed===true;message.className='password-change-message success';message.textContent=data.message;message.focus();if(changed){form.querySelectorAll('input').forEach(node=>node.disabled=true);cancel.textContent='닫기';}}
  catch(error){form.reset();message.className='password-change-message error';message.textContent=error.message;message.focus();}
  finally{submit.disabled=false;cancel.disabled=false;submit.textContent=changed?'로그인하기':'비밀번호 변경';}
 });
}

__BOOKMARKS_SCRIPT__
</script>__CC_SCRIPT__
</body></html>'''
