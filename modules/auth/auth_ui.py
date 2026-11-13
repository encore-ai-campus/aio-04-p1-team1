"""두 페이지가 공유하는 디자인과 브라우저 동작."""

import json

from fastapi.responses import HTMLResponse
from shared.components.compass import common_css
from shared.components.loading import apply_loading


def render_auth(page="signin", main_path=None):
    signup = page == "signup"
    title = "나의 다음 걸음, 함께 찾아요" if signup else "다시 만나 반가워요"
    subtitle = "취준나침반과 함께 나에게 맞는 기회를 발견하세요." if signup else "저장한 기회와 나의 준비를 이어서 확인해 보세요."
    fields = '''<div class="field"><label for="name">이름</label><input id="name" name="name" autocomplete="name" placeholder="이름을 입력해 주세요" minlength="2" maxlength="30" required></div>''' if signup else ""
    confirmation = '''<div class="field"><label for="password_confirm">비밀번호 확인</label><div class="password-box"><input id="password_confirm" name="password_confirm" type="password" autocomplete="new-password" placeholder="비밀번호를 한 번 더 입력해 주세요" minlength="8" maxlength="128" required><button type="button" class="reveal" data-target="password_confirm" aria-label="비밀번호 확인 표시">보기</button></div></div>''' if signup else ""
    return HTMLResponse(apply_loading(TEMPLATE.replace("__TITLE__", title).replace("__SUBTITLE__", subtitle)
                        .replace("__NAME_FIELD__", fields).replace("__CONFIRM_FIELD__", confirmation)
                        .replace("__PAGE__", page).replace("__SUCCESS_PATH__", json.dumps(main_path))
                        .replace("__CC_CSS__", common_css())
                        .replace("__ACTION__", "회원가입" if signup else "로그인")
                        .replace("__AUTOCOMPLETE__", "new-password" if signup else "current-password")
                        .replace("__MINLENGTH__", "8" if signup else "1")
                        .replace("__HELP__", "영문과 숫자를 포함해 8~128자로 입력해 주세요." if signup else "가입할 때 사용한 비밀번호를 입력해 주세요.")
                        .replace("__FOOTER__", '이미 계정이 있나요? <a href="/signin">로그인</a>' if signup else '아직 계정이 없나요? <a href="/signup">회원가입</a>')))


TEMPLATE = r'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__ACTION__ · 취준나침반</title>
<style>
:root{--ink:var(--cc-text);--muted:var(--cc-muted);--yellow:var(--cc-yellow);--cream:var(--cc-background);--line:var(--cc-border)}
*{box-sizing:border-box}body{margin:0;min-height:100vh;min-height:100dvh;display:flex;flex-direction:column;font-family:var(--cc-font);background:var(--cream);color:var(--ink)}
a{color:inherit}button,input{font:inherit}button,a,input{ -webkit-tap-highlight-color:transparent}a:focus-visible,button:focus-visible{outline:3px solid #526d43;outline-offset:4px}
header{width:100%;max-width:1320px;margin:0 auto;padding:32px 24px 24px;display:flex;justify-content:center;flex-shrink:0}.brand{display:flex;align-items:center;gap:16px;text-decoration:none}.brand-icon{display:block;flex-shrink:0;width:76px;height:76px;color:#88522f}.brand svg{display:block;width:100%;height:100%}.brand-copy{display:flex;flex-direction:column;gap:8px}.brand-title{font-size:36px;line-height:1.2;letter-spacing:-1.5px;font-weight:400}.header-note{font-size:14px;line-height:1.6;color:var(--muted);word-break:keep-all}
main{width:calc(100% - 32px);max-width:520px;margin:12px auto 32px;border:1px solid var(--line);border-radius:28px;overflow:hidden;background:white;box-shadow:0 16px 60px #26312705}
.form-side{padding:40px 44px;display:flex;flex-direction:column;justify-content:center}.tabs{display:flex;gap:24px;border-bottom:1px solid var(--line);margin-bottom:27px}.tabs a{font-size:13px;text-decoration:none;padding:0 0 13px;color:#94978b}.tabs a.active{color:var(--ink);font-weight:400;border-bottom:2px solid var(--ink)}.form-side h2{font-size:25px;line-height:1.5;letter-spacing:-1.2px;margin:0 0 8px}.subtitle{font-size:12px;line-height:1.8;color:var(--muted);margin:0 0 27px}.field{margin-bottom:17px}label{display:block;font-size:12px;font-weight:400;margin-bottom:8px}input{width:100%;height:47px;border:1px solid #dedfd7;border-radius:9px;padding:0 14px;background:white;font-size:13px;color:var(--ink);transition:border-color .2s,box-shadow .2s}input::placeholder{color:#a0a398;font-size:12px}input:focus{outline:none;border-color:#a59a4b;box-shadow:0 0 0 3px #f7ca4326}.password-box{position:relative}.password-box input{padding-right:58px}.reveal{position:absolute;right:12px;top:0;height:47px;background:none;border:0;font-size:11px;color:#757969;cursor:pointer}.help{font-size:10px;line-height:1.6;color:#85897c;margin:7px 0 0}.submit{width:100%;height:49px;border:0;border-radius:10px;background:var(--yellow);color:#303522;font-size:13px;font-weight:400;cursor:pointer;display:flex;align-items:center;justify-content:space-between;padding:0 18px;margin-top:23px;transition:background .2s,transform .2s}.submit:hover{background:#efbd2e;transform:translateY(-1px)}.submit:disabled{opacity:.6;cursor:wait;transform:none}.message{display:none;padding:12px 14px;border-radius:9px;font-size:12px;line-height:1.7;margin:15px 0 0}.message.error{display:block;background:#fff0ec;color:#a73c28;border:1px solid #f3d4ca}.message.success{display:block;background:#f1f6e9;color:#436035;border:1px solid #d9e6c8}.form-footer{font-size:11px;text-align:center;color:var(--muted);margin:23px 0 0}.form-footer a{font-weight:400;margin-left:7px;text-underline-offset:4px}.account{border:1px solid #dee6d4;background:#f6f9ef;padding:24px;border-radius:15px}.account h3{margin:0 0 12px;font-size:20px}.account p{font-size:13px;line-height:1.8;overflow-wrap:anywhere}.account button{width:100%;margin-top:14px;padding:12px;border:1px solid #d3d8c8;border-radius:9px;background:white;cursor:pointer}.account a{display:block;font-size:12px;margin-top:16px;text-underline-offset:4px}footer{text-align:center;font-size:10px;letter-spacing:.3px;color:#95998c;padding:0 20px 26px}.noscript{padding:20px;background:#fff0ec}.hidden{display:none!important}
@media(min-height:820px){main{margin:12px auto 32px}footer{margin-top:auto;padding-top:32px}}
@media(max-width:700px){header{padding:26px 20px 18px}.brand{gap:12px}.brand-icon{width:60px;height:60px}.brand-copy{gap:6px}.brand-title{font-size:29px}.header-note{font-size:12px;max-width:240px}main{border-radius:21px}.form-side{padding:30px 25px}.form-side h2{font-size:23px}.subtitle{font-size:11px;margin-bottom:23px}footer{font-size:9px}}
__CC_CSS__
.cc-member-page .brand-title{font-weight:600}
</style>
</head>
<body class="cc-member-page cc-auth-page" data-page="__PAGE__">
<header><a class="brand" href="/signin"><span class="brand-icon" aria-hidden="true"><svg class="cc-brand-mark" viewBox="0 0 44 44" aria-hidden="true">
          <circle cx="22" cy="22" r="21" fill="#f7ca43"/>
          <path d="m31 10-5 16-13 8 5-16Z" fill="#263127"/>
          <path d="m31 10-9 12-4-4Z" fill="#fffaf0"/>
        </svg></span><span class="brand-copy"><span class="brand-title">취준나침반</span><span class="header-note">취업의 길, 한 번에 찾고, 한 걸음씩 함께 나아가요</span></span></a></header>
<main>
<section class="form-side" aria-labelledby="form-title"><nav class="tabs" aria-label="회원 메뉴"><a href="/signin" data-tab="signin">로그인</a><a href="/signup" data-tab="signup">회원가입</a></nav>
<div id="form-content"><h2 id="form-title">__TITLE__</h2><p class="subtitle">__SUBTITLE__</p>
<form id="auth-form">__NAME_FIELD__<div class="field"><label for="email">이메일</label><input id="email" name="email" type="email" autocomplete="email" placeholder="example@email.com" maxlength="254" required></div>
<div class="field"><label for="password">비밀번호</label><div class="password-box"><input id="password" name="password" type="password" autocomplete="__AUTOCOMPLETE__" placeholder="비밀번호를 입력해 주세요" minlength="__MINLENGTH__" maxlength="128" required><button class="reveal" type="button" data-target="password" aria-label="비밀번호 표시">보기</button></div><p class="help" id="password-help">__HELP__</p></div>
__CONFIRM_FIELD__<button id="submit" class="submit" type="submit"><span>__ACTION__</span><span aria-hidden="true">→</span></button></form>
<div id="message" class="message" role="status" aria-live="polite" tabindex="-1"></div><p class="form-footer">__FOOTER__</p></div>
<div id="account" class="account hidden"><h3 id="welcome"></h3><p id="account-email"></p><p>로그인되었습니다.<br>나에게 맞는 다음 기회를 준비해 보세요.</p><button id="signout" type="button">로그아웃</button><a href="/docs">API 문서 확인하기 ↗</a><p id="account-message" role="status" aria-live="polite"></p></div>
</section></main><footer>© 2026 취준나침반 · 당신의 다음 걸음을 응원합니다.</footer>
<noscript><p class="noscript">회원가입과 로그인을 이용하려면 JavaScript를 활성화해 주세요.</p></noscript>
<script>
const page=document.body.dataset.page;
document.querySelector(`[data-tab="${page}"]`).classList.add('active');
document.querySelector(`[data-tab="${page}"]`).setAttribute('aria-current','page');
document.getElementById('password').setAttribute('aria-describedby','password-help');
document.querySelectorAll('.reveal').forEach(button=>button.addEventListener('click',()=>{const input=document.getElementById(button.dataset.target);const show=input.type==='password';input.type=show?'text':'password';button.textContent=show?'숨김':'보기';button.setAttribute('aria-pressed',String(show));}));
const form=document.getElementById('auth-form'),submit=document.getElementById('submit'),message=document.getElementById('message');
function showMessage(text,type){message.textContent=text;message.className='message '+type;message.focus();}
function showAccount(user){const mainPath=__SUCCESS_PATH__;if(mainPath){window.CompassLoading.navigate(mainPath,'login');return;}window.CompassLoading.hide();document.getElementById('form-content').classList.add('hidden');document.getElementById('account').classList.remove('hidden');document.getElementById('welcome').textContent=user.name+'님, 반가워요!';document.getElementById('account-email').textContent=user.email;}
form.addEventListener('submit',async event=>{
 event.preventDefault();message.className='message';const data=Object.fromEntries(new FormData(form));
 if(page==='signup'){
  if(data.name.trim().length<2){showMessage('이름은 공백을 제외하고 2자 이상 입력해 주세요.','error');return;}
  if(!/[A-Za-z]/.test(data.password)||!/[0-9]/.test(data.password)){showMessage('비밀번호는 영문과 숫자를 모두 포함해 주세요.','error');return;}
  if(data.password!==data.password_confirm){showMessage('비밀번호 확인이 일치하지 않습니다.','error');return;}
 }
 submit.disabled=true;submit.firstElementChild.textContent='처리 중…';
 let navigating=false;if(page==='signin')window.CompassLoading.show('login');
 try{
  const response=await fetch('/api/auth/'+page,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  const result=await response.json();if(!response.ok){showMessage(typeof result.detail==='string'?result.detail:'입력값을 확인해 주세요.','error');return;}
  form.reset();
  if(page==='signup'){showMessage(result.message,'success');}
  else{navigating=Boolean(__SUCCESS_PATH__);showAccount(result);}
 }catch(error){showMessage('서버에 연결하지 못했습니다. 잠시 후 다시 시도해 주세요.','error');}
 finally{if(page==='signin'&&!navigating)window.CompassLoading.hide();submit.disabled=false;submit.firstElementChild.textContent=page==='signup'?'회원가입':'로그인';}
});
document.getElementById('signout').addEventListener('click',async()=>{const button=document.getElementById('signout');button.disabled=true;try{const response=await fetch('/api/auth/signout',{method:'POST'});if(!response.ok)throw new Error();location.assign('/signin');}catch(error){document.getElementById('account-message').textContent='로그아웃하지 못했습니다. 다시 시도해 주세요.';button.disabled=false;}});
if(page==='signin'){
 const query=new URLSearchParams(location.search);
 if(query.has('confirmed'))showMessage('이메일 인증 결과를 확인한 후 로그인해 주세요.','success');
 if(query.has('confirmation_error'))showMessage('인증 링크가 만료되었거나 유효하지 않습니다. 받은 인증 메일을 확인해 주세요.','error');
 fetch('/api/auth/me').then(response=>response.ok?response.json():null).then(user=>{if(user)showAccount(user);}).catch(()=>{});
}
</script></body></html>'''
