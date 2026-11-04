"""page로 이동"""
import json

from fastapi.responses import HTMLResponse


def render_auth(page="signin", main_path=None):
    signup = page == "signup"
    title = "나의 다음 걸음, 함께 찾아요" if signup else "다시 만나 반가워요"
    subtitle = "취준나침반과 함께 나에게 맞는 기회를 발견하세요." if signup else "저장한 기회와 나의 준비를 이어서 확인해 보세요."
    fields = '''<div class="field"><label for="name">이름</label><input id="name" name="name" autocomplete="name" placeholder="이름을 입력해 주세요" minlength="2" maxlength="30" required></div>''' if signup else ""
    confirmation = '''<div class="field"><label for="password_confirm">비밀번호 확인</label><div class="password-box"><input id="password_confirm" name="password_confirm" type="password" autocomplete="new-password" placeholder="비밀번호를 한 번 더 입력해 주세요" minlength="8" maxlength="128" required><button type="button" class="reveal" data-target="password_confirm" aria-label="비밀번호 확인 표시">보기</button></div></div>''' if signup else ""
    return HTMLResponse(TEMPLATE.replace("__TITLE__", title).replace("__SUBTITLE__", subtitle)
                        .replace("__NAME_FIELD__", fields).replace("__CONFIRM_FIELD__", confirmation)
                        .replace("__PAGE__", page).replace("__SUCCESS_PATH__", json.dumps(main_path))
                        .replace("__ACTION__", "회원가입" if signup else "로그인")
                        .replace("__AUTOCOMPLETE__", "new-password" if signup else "current-password")
                        .replace("__MINLENGTH__", "8" if signup else "1")
                        .replace("__HELP__", "영문과 숫자를 포함해 8~128자로 입력해 주세요." if signup else "가입할 때 사용한 비밀번호를 입력해 주세요.")
                        .replace("__FOOTER__", '이미 계정이 있나요? <a href="/signin">로그인</a>' if signup else '아직 계정이 없나요? <a href="/signup">회원가입</a>'))


TEMPLATE = r'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__ACTION__ · 취준나침반</title>
<style>
:root{--ink:#263127;--muted:#74786e;--yellow:#f7ca43;--cream:#faf9f5;--line:#e5e6df}
*{box-sizing:border-box}body{margin:0;font-family:"Malgun Gothic","Apple SD Gothic Neo",sans-serif;background:var(--cream);color:var(--ink)}
a{color:inherit}button,input{font:inherit}button,a,input{ -webkit-tap-highlight-color:transparent}a:focus-visible,button:focus-visible{outline:3px solid #526d43;outline-offset:4px}
header{height:88px;max-width:1320px;margin:auto;padding:0 56px;display:flex;align-items:center;justify-content:space-between}.brand{display:flex;align-items:center;gap:11px;font-size:20px;letter-spacing:-1px;text-decoration:none;font-weight:800}.brand-icon{display:grid;place-items:center;width:34px;height:34px;border:1.5px solid var(--ink);border-radius:50%;background:var(--yellow)}.brand svg{width:23px;height:23px}.header-note{font-size:12px;color:var(--muted)}
main{max-width:1208px;margin:24px auto 40px;display:grid;grid-template-columns:1fr 1fr;min-height:720px;border:1px solid var(--line);border-radius:28px;overflow:hidden;background:white;box-shadow:0 16px 60px #26312705}
.story{position:relative;background:#f5efcf;padding:56px 48px;display:flex;flex-direction:column;overflow:hidden}.eyebrow{font-size:11px;font-weight:800;letter-spacing:2.5px;display:flex;align-items:center;gap:9px}.eyebrow:before{content:"";width:7px;height:7px;background:#79905d;border-radius:50%}.story h1{font-size:39px;line-height:1.5;letter-spacing:-2px;margin:27px 0 14px}.story h1 span{background:linear-gradient(transparent 60%,#f7ca4388 0)}.story p{font-size:14px;line-height:1.95;color:#626755;margin:0}.illustration{position:relative;height:230px;margin:20px 0 10px;display:grid;place-items:center}.orbit{position:absolute;width:235px;height:235px;border:1px dashed #c5c1a3;border-radius:50%;transform:rotate(-25deg)}.orbit:after{content:"";position:absolute;inset:25px;border:1px solid #ded9bb;border-radius:50%}.compass{width:145px;height:145px;background:#fffcf0;border:8px solid #fff9e5;border-radius:50%;box-shadow:0 12px 32px #746d3420;display:grid;place-items:center;transform:rotate(12deg);position:relative}.compass svg{width:110px;height:110px}.tag{position:absolute;padding:10px 14px;background:white;border:1px solid #eae6d7;border-radius:12px;font-size:12px;box-shadow:0 5px 16px #6b633409}.tag.one{left:2px;top:34px;transform:rotate(-7deg)}.tag.two{right:0;bottom:30px;transform:rotate(6deg)}.star{position:absolute;right:35px;top:30px;font-size:24px;color:#aa9752}.steps{display:flex;gap:8px;margin-top:auto;padding-top:18px}.step{font-size:11px;padding:9px 10px;border:1px solid #ded7b3;border-radius:20px;background:#fbf7e7}.story-foot{font-size:11px;color:#838570;margin-top:25px}
.form-side{padding:48px 54px;display:flex;flex-direction:column;justify-content:center}.tabs{display:flex;gap:24px;border-bottom:1px solid var(--line);margin-bottom:27px}.tabs a{font-size:13px;text-decoration:none;padding:0 0 13px;color:#94978b}.tabs a.active{color:var(--ink);font-weight:800;border-bottom:2px solid var(--ink)}.form-side h2{font-size:25px;line-height:1.5;letter-spacing:-1.2px;margin:0 0 8px}.subtitle{font-size:12px;line-height:1.8;color:var(--muted);margin:0 0 27px}.field{margin-bottom:17px}label{display:block;font-size:12px;font-weight:700;margin-bottom:8px}input{width:100%;height:47px;border:1px solid #dedfd7;border-radius:9px;padding:0 14px;background:white;font-size:13px;color:var(--ink);transition:border-color .2s,box-shadow .2s}input::placeholder{color:#a0a398;font-size:12px}input:focus{outline:none;border-color:#a59a4b;box-shadow:0 0 0 3px #f7ca4326}.password-box{position:relative}.password-box input{padding-right:58px}.reveal{position:absolute;right:12px;top:0;height:47px;background:none;border:0;font-size:11px;color:#757969;cursor:pointer}.help{font-size:10px;line-height:1.6;color:#85897c;margin:7px 0 0}.submit{width:100%;height:49px;border:0;border-radius:10px;background:var(--yellow);color:#303522;font-size:13px;font-weight:800;cursor:pointer;display:flex;align-items:center;justify-content:space-between;padding:0 18px;margin-top:23px;transition:background .2s,transform .2s}.submit:hover{background:#efbd2e;transform:translateY(-1px)}.submit:disabled{opacity:.6;cursor:wait;transform:none}.message{display:none;padding:12px 14px;border-radius:9px;font-size:12px;line-height:1.7;margin:15px 0 0}.message.error{display:block;background:#fff0ec;color:#a73c28;border:1px solid #f3d4ca}.message.success{display:block;background:#f1f6e9;color:#436035;border:1px solid #d9e6c8}.form-footer{font-size:11px;text-align:center;color:var(--muted);margin:23px 0 0}.form-footer a{font-weight:800;margin-left:7px;text-underline-offset:4px}.privacy-note{border-top:1px solid var(--line);margin-top:26px;padding-top:18px;color:#96998e;font-size:10px;line-height:1.8}.account{border:1px solid #dee6d4;background:#f6f9ef;padding:24px;border-radius:15px}.account h3{margin:0 0 12px;font-size:20px}.account p{font-size:13px;line-height:1.8;overflow-wrap:anywhere}.account button{width:100%;margin-top:14px;padding:12px;border:1px solid #d3d8c8;border-radius:9px;background:white;cursor:pointer}.account a{display:block;font-size:12px;margin-top:16px;text-underline-offset:4px}footer{text-align:center;font-size:10px;letter-spacing:.3px;color:#95998c;padding:0 20px 26px}.noscript{padding:20px;background:#fff0ec}.hidden{display:none!important}
@media(min-width:1300px){main{margin-top:35px}}@media(max-width:1000px){main{margin:15px 24px 30px}.story{padding:42px 30px}.form-side{padding:40px 32px}.story h1{font-size:32px}.tag{font-size:10px;padding:9px}.steps{flex-wrap:wrap}}
@media(max-width:700px){header{height:74px;padding:0 24px}.brand{font-size:18px}.header-note{display:none}main{display:block;min-height:0;margin:4px 16px 25px;border-radius:21px}.story{padding:28px 26px}.eyebrow{font-size:9px}.story h1{font-size:27px;margin:15px 0 8px;line-height:1.4}.story p{font-size:12px}.illustration,.steps,.story-foot{display:none}.form-side{padding:30px 25px 35px}.form-side h2{font-size:23px}.subtitle{font-size:11px;margin-bottom:23px}footer{font-size:9px}}
</style>
</head>
<body data-page="__PAGE__">
<header><a class="brand" href="/signin"><span class="brand-icon" aria-hidden="true"><svg viewBox="0 0 32 32"><path d="M23 8 18 19 8 24 13 13Z" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="m23 8-7 8-3-3Z" fill="currentColor"/></svg></span>취준나침반</a><span class="header-note">한 번에 찾고, 한 걸음씩 준비해요.</span></header>
<main>
<section class="story" aria-label="취준나침반 소개"><div class="eyebrow">YOUR NEXT DIRECTION</div><h1>막막했던 취업 준비,<br><span>나만의 방향</span>을 찾다.</h1><p>나에게 맞는 공고부터 다음에 필요한 배움까지.<br>당신의 다음 걸음에 취준나침반이 함께할게요.</p>
<div class="illustration" aria-hidden="true"><div class="orbit"></div><span class="star">✧</span><div class="compass"><svg viewBox="0 0 120 120"><circle cx="60" cy="60" r="49" fill="none" stroke="#d8d2b5"/><text x="56" y="21" font-size="9" fill="#878a73">N</text><path d="m80 35-12 37-28 13 12-37Z" fill="#f7ca43"/><path d="m80 35-20 25-8-12Z" fill="#4d6242"/><path d="m40 85 20-25 8 12Z" fill="#fff4c6"/><circle cx="60" cy="60" r="4" fill="#4d6242"/></svg></div><span class="tag one">↗ 나에게 맞는 기회</span><span class="tag two">✦ 한 걸음 더 성장하기</span></div>
<div class="steps"><span class="step">01 공고 찾기</span><span class="step">02 준비 상태 비교</span><span class="step">03 다음 배움 찾기</span></div><div class="story-foot">각자의 속도로, 더 선명한 내일을 향해.</div></section>
<section class="form-side" aria-labelledby="form-title"><nav class="tabs" aria-label="회원 메뉴"><a href="/signin" data-tab="signin">로그인</a><a href="/signup" data-tab="signup">회원가입</a></nav>
<div id="form-content"><h2 id="form-title">__TITLE__</h2><p class="subtitle">__SUBTITLE__</p>
<form id="auth-form">__NAME_FIELD__<div class="field"><label for="email">이메일</label><input id="email" name="email" type="email" autocomplete="email" placeholder="example@email.com" maxlength="254" required></div>
<div class="field"><label for="password">비밀번호</label><div class="password-box"><input id="password" name="password" type="password" autocomplete="__AUTOCOMPLETE__" placeholder="비밀번호를 입력해 주세요" minlength="__MINLENGTH__" maxlength="128" required><button class="reveal" type="button" data-target="password" aria-label="비밀번호 표시">보기</button></div><p class="help" id="password-help">__HELP__</p></div>
__CONFIRM_FIELD__<button id="submit" class="submit" type="submit"><span>__ACTION__</span><span aria-hidden="true">→</span></button></form>
<div id="message" class="message" role="status" aria-live="polite" tabindex="-1"></div><p class="form-footer">__FOOTER__</p></div>
<div id="account" class="account hidden"><h3 id="welcome"></h3><p id="account-email"></p><p>로그인되었습니다.<br>나에게 맞는 다음 기회를 준비해 보세요.</p><button id="signout" type="button">로그아웃</button><a href="/docs">API 문서 확인하기 ↗</a><p id="account-message" role="status" aria-live="polite"></p></div>
<p class="privacy-note">취업 준비의 시작부터 다음 걸음까지,<br>필요한 정보를 한곳에서 확인하세요.</p>
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
function showAccount(user){const mainPath=__SUCCESS_PATH__;if(mainPath){location.assign(mainPath);return;}document.getElementById('form-content').classList.add('hidden');document.getElementById('account').classList.remove('hidden');document.getElementById('welcome').textContent=user.name+'님, 반가워요!';document.getElementById('account-email').textContent=user.email;}
form.addEventListener('submit',async event=>{
 event.preventDefault();message.className='message';const data=Object.fromEntries(new FormData(form));
 if(page==='signup'){
  if(data.name.trim().length<2){showMessage('이름은 공백을 제외하고 2자 이상 입력해 주세요.','error');return;}
  if(!/[A-Za-z]/.test(data.password)||!/[0-9]/.test(data.password)){showMessage('비밀번호는 영문과 숫자를 모두 포함해 주세요.','error');return;}
  if(data.password!==data.password_confirm){showMessage('비밀번호 확인이 일치하지 않습니다.','error');return;}
 }
 submit.disabled=true;submit.firstElementChild.textContent='처리 중…';
 try{
  const response=await fetch('/api/auth/'+page,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  const result=await response.json();if(!response.ok){showMessage(typeof result.detail==='string'?result.detail:'입력값을 확인해 주세요.','error');return;}
  form.reset();
  if(page==='signup'){showMessage('회원가입이 완료되었습니다. 로그인 화면으로 이동합니다.','success');setTimeout(()=>location.assign('/signin?registered=1'),1200);}
  else{showAccount(result);}
 }catch(error){showMessage('서버에 연결하지 못했습니다. 잠시 후 다시 시도해 주세요.','error');}
 finally{submit.disabled=false;submit.firstElementChild.textContent=page==='signup'?'회원가입':'로그인';}
});
document.getElementById('signout').addEventListener('click',async()=>{const button=document.getElementById('signout');button.disabled=true;try{const response=await fetch('/api/auth/signout',{method:'POST'});if(!response.ok)throw new Error();location.assign('/signin');}catch(error){document.getElementById('account-message').textContent='로그아웃하지 못했습니다. 다시 시도해 주세요.';button.disabled=false;}});
if(page==='signin'){
 if(new URLSearchParams(location.search).has('registered'))showMessage('회원가입이 완료되었습니다. 로그인해 주세요.','success');
 fetch('/api/auth/me').then(response=>response.ok?response.json():null).then(user=>{if(user)showAccount(user);}).catch(()=>{});
}
</script></body></html>'''
