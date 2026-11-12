"""시안 기반 마이페이지: 개인정보 요약, 관심목록, 프로필 편집."""

from html import escape
from fastapi.responses import HTMLResponse
from shared.components.compass import apply_member_shell
from modules.mypage.skills_ui import apply_skills_ui
from modules.mypage.bookmarks_ui import CONTENT as BOOKMARKS_CONTENT, SCRIPT as BOOKMARKS_SCRIPT, CSS as BOOKMARKS_CSS


def render_dashboard(user):
    template = TEMPLATE.replace("__BOOKMARKS_CONTENT__", BOOKMARKS_CONTENT).replace("__BOOKMARKS_SCRIPT__", BOOKMARKS_SCRIPT).replace("__BOOKMARKS_CSS__", BOOKMARKS_CSS)
    html = template.replace("__NAME__", escape(user["name"], quote=True)).replace("__EMAIL__", escape(user["email"], quote=True))
    html = apply_skills_ui(html, user)
    return HTMLResponse(apply_member_shell(html, user, 'mypage'))


TEMPLATE = r'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>마이페이지 · 취준나침반</title><style>
:root{--ink:var(--cc-text);--muted:var(--cc-muted);--yellow:var(--cc-yellow);--cream:var(--cc-background);--line:var(--cc-border);--pale:#fff6d7}
*{box-sizing:border-box}body{margin:0;color:var(--ink);background:var(--cream);font-family:var(--cc-font)}button,input,select{font:inherit}a{color:inherit;text-decoration:none}button,a,input,select,summary{touch-action:manipulation}button,summary{cursor:pointer}a:focus-visible,button:focus-visible,summary:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #93823c;outline-offset:3px}button:disabled{opacity:.5;cursor:wait}
header{background:white;border-bottom:1px solid var(--line)}.header-inner{max-width:1280px;min-height:84px;margin:auto;padding:18px 28px;display:flex;align-items:center;justify-content:space-between;gap:24px}.brand{display:flex;align-items:center;gap:10px;font-size:25px;font-weight:400;letter-spacing:-1px}.brand-icon{font-size:35px}.header-nav{display:flex;align-items:center;gap:22px;font-size:13px}.header-nav .current{padding:12px 23px;background:var(--yellow);border-radius:10px;font-weight:400}
.container{max-width:1280px;margin:32px auto;padding:0 28px}.eyebrow{font-size:10px;color:var(--muted);font-weight:400;letter-spacing:1px}h1{font-size:30px;margin:18px 0 12px;letter-spacing:-1px}.intro{font-size:14px;line-height:1.8;color:var(--muted);margin-bottom:26px}.layout{display:grid;grid-template-columns:250px minmax(0,1fr);gap:24px;align-items:start}.panel{background:white;border:1px solid var(--line);border-radius:16px;padding:24px}.sidebar{padding:24px;display:flex;flex-direction:column;min-height:650px}.avatar{width:48px;height:48px;display:grid;place-items:center;border-radius:50%;background:var(--pale);color:#718656;font-size:31px}.user-name{font-size:23px;font-weight:400;margin:18px 0 10px;overflow-wrap:anywhere}.role{font-size:13px;line-height:1.7;color:var(--muted);margin:0 0 16px}.status-pill{background:#edf3e5;color:#688151;border-radius:18px;font-size:11px;padding:7px 13px;align-self:start}.side-nav{display:grid;gap:10px;border-top:1px solid var(--line);margin-top:26px;padding-top:22px}.side-nav a{padding:14px 12px;border-radius:10px;font-size:13px;font-weight:400;display:flex;justify-content:space-between;gap:10px}.side-nav .active{background:var(--pale)}.counts{padding:0 12px;font-size:12px;line-height:2.3;color:var(--muted)}.side-note{font-size:12px;line-height:1.9;color:var(--muted);border-top:1px solid var(--line);padding-top:20px;margin-top:24px}.back{margin-top:auto;padding-top:38px}.button{display:inline-flex;align-items:center;justify-content:center;padding:10px 18px;border:1px solid var(--line);border-radius:9px;font-size:12px;background:white;color:var(--ink)}.button:hover{border-color:#bcab63}.primary{background:var(--yellow);border-color:var(--yellow);font-weight:400}.back .button{width:100%}.content{display:grid;gap:20px}.section-head{display:flex;align-items:center;justify-content:space-between;gap:16px}h2{font-size:20px;margin:0;letter-spacing:-.6px}.section-note{font-size:12px;color:var(--muted);line-height:1.8;margin:12px 0 24px}.info-grid{display:grid;grid-template-columns:1fr 1fr;gap:26px;margin:28px 0 8px}.info-grid dt{font-size:11px;color:var(--muted);margin-bottom:12px}.info-grid dd{font-size:15px;line-height:1.7;margin:0;overflow-wrap:anywhere}.subtle{color:var(--muted);font-size:12px!important}
details{border-bottom:1px solid var(--line)}details:last-child{border:0}summary{list-style:none;display:flex;align-items:center;gap:18px;min-height:62px;padding:16px;font-size:15px;font-weight:400;border-radius:10px}summary::-webkit-details-marker{display:none}summary:after{content:'⌄';margin-left:auto;color:#688151}details[open]>summary{background:var(--pale)}details[open]>summary:after{content:'⌃'}.summary-note{font-size:11px;font-weight:400;color:var(--muted);line-height:1.7}.entries{padding:12px 16px}.entry{padding:16px 0;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;gap:16px}.entry:last-child{border:0}.entry h3{font-size:15px;margin:0 0 8px;overflow-wrap:anywhere}.entry p{font-size:12px;color:var(--muted);line-height:1.8;margin:0;overflow-wrap:anywhere}.entry-actions{display:flex;gap:6px;flex-shrink:0}.entry-actions button{padding:7px 10px}.empty{font-size:12px;line-height:1.9;color:var(--muted);padding:8px 0}.add{width:100%;margin:8px 0 18px;color:#5c7548;font-weight:400}.profile-data-tools{display:flex;align-items:center;gap:10px}.flash{font-size:12px;line-height:1.8;min-height:22px}.error{color:#a73c28}.success{color:#4c6b38}.loading{opacity:.65;pointer-events:none}footer{text-align:center;padding:24px;font-size:10px;color:var(--muted)}
dialog{width:calc(100% - 32px);max-width:500px;max-height:85vh;overflow:auto;border:1px solid var(--line);border-radius:18px;padding:28px;color:var(--ink);box-shadow:0 20px 70px #26312726}dialog::backdrop{background:#26312766}dialog h2{margin-bottom:22px}.field{display:grid;gap:8px;margin-bottom:18px}.field label{font-size:12px;font-weight:400}input,select{width:100%;min-width:0;height:44px;padding:0 12px;border:1px solid var(--line);border-radius:8px;background:white;color:var(--ink);font-size:13px}.dialog-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:22px}.dialog-status{font-size:12px;color:#a73c28;line-height:1.8}.hidden{display:none!important}
@media(max-width:800px){.header-inner{padding:16px 20px;flex-wrap:wrap}.brand{font-size:22px}.header-nav{gap:12px;font-size:12px}.header-nav .username{display:none}.container{padding:0 16px;margin-top:24px}.layout{grid-template-columns:1fr}.sidebar{min-height:0;padding:20px}.avatar,.side-note,.back{display:none}.user-name{margin-top:0}.side-nav{margin-top:18px;padding-top:14px;grid-template-columns:1fr 1fr}.counts{display:flex;gap:18px}.status-pill{font-size:10px}.panel{padding:20px}.info-grid{gap:20px}.section-head{flex-wrap:wrap}.entry{align-items:start;flex-direction:column}.summary-note{max-width:60%}h1{font-size:26px}}
@media(prefers-reduced-motion:no-preference){dialog[open]{animation:appear .15s ease-out}@keyframes appear{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}}
__BOOKMARKS_CSS__
#profile-overview,#bookmarks{scroll-margin-top:24px}#bookmarks{margin-top:16px;padding-bottom:24px}.sidebar{position:sticky;top:16px;max-height:calc(100dvh - 32px);overflow-y:auto}.side-nav a:hover{background:var(--pale)}
@media(max-width:800px){.sidebar{top:0;z-index:5;min-height:0;padding:10px 16px;box-shadow:0 5px 16px #2631270a}.sidebar .user-name,.sidebar .role,.sidebar .status-pill{display:none}.side-nav{margin:0;padding:0;border:0}.side-nav a{padding:10px 8px}.counts{font-size:10px;line-height:1.8}#profile-overview,#bookmarks{scroll-margin-top:112px}}
__CC_CSS__
__SKILLS_CSS__
.profile-skills .skills-section{margin-top:0;padding-top:0;border-top:0}#editor-fields>label{display:block;font-size:12px;margin-bottom:8px}#editor .skills-input-row .button{flex-shrink:0;min-height:44px}#roles-list:empty{display:none}

.profile-item{position:relative;border-bottom:1px solid var(--line)}
.profile-item>details{border:0}
#profile-data-content summary{position:relative;min-height:72px;padding:18px 16px;gap:12px;font-size:18px;line-height:1.6;letter-spacing:-.3px;background:transparent}
#profile-data-content details[open]>summary{background:transparent}
#profile-data-content summary::after{content:"";display:block;flex:0 0 32px;width:32px;height:32px;border:1px solid #ccd5bd;border-radius:50%;background:#f4f7ee url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='m6 9 6 6 6-6' fill='none' stroke='%23536843' stroke-width='2.3' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/16px 16px no-repeat;margin-left:auto;transition:transform .15s ease}
#profile-data-content details[open]>summary::after{content:"";transform:rotate(180deg)}
#profile-data-content .profile-item-editable summary{padding-right:188px}
#profile-data-content .profile-item-editable summary::after{position:absolute;right:144px;top:20px;margin:0}
.profile-edit-button{position:absolute;right:16px;top:20px;min-width:112px;min-height:32px;padding:6px 10px;font-size:12px;line-height:1.5}
.profile-information .skills-tags{gap:12px;margin:14px 0 12px}
.profile-information .skills-tag{padding:10px 16px;border-color:#e0e4da;border-radius:12px;font-size:18px;line-height:1.5}
.profile-information .skills-tag-hash{color:#8b917f;margin-right:5px}
.profile-information .skills-help{font-size:14px;line-height:1.8;margin:12px 0;color:var(--cc-muted)}
.profile-information .entries{padding:0 16px 20px}
@media(max-width:620px){#profile-data-content summary{font-size:16px;padding:18px 12px}#profile-data-content .profile-item-editable summary{padding-right:168px}#profile-data-content .profile-item-editable .summary-note{display:none}#profile-data-content .profile-item-editable summary::after{width:28px;height:28px;right:130px;top:21px}.profile-edit-button{min-width:108px;right:12px;top:20px;font-size:11px}.profile-information .skills-tags{gap:8px}.profile-information .skills-tag{font-size:16px;padding:9px 12px}.profile-information .skills-help{font-size:12px}.profile-information .entries{padding:0 12px 18px}}
</style></head><body class="cc-member-page">
__CC_HEADER__
__CC_MENU__
<div class="container cc-page" data-member-content><section class="cc-page-heading"><p class="eyebrow">YOUR NEXT DIRECTION</p><h1>마이페이지</h1><p class="intro">개인정보와 프로필 정보를 한곳에서 관리하고, 필요한 항목을 펼쳐 수정해요.</p></section>
<div class="layout"><aside class="panel sidebar"><span class="avatar" aria-hidden="true">◎</span><div class="user-name">__NAME__님</div><p id="target-role" class="role">희망 직무를 입력해 보세요.</p><nav class="side-nav" aria-label="마이페이지 메뉴"><a class="active" href="#profile-overview" data-section="profile-overview" aria-current="location">개인정보 · 프로필 정보</a><a href="#bookmarks" data-section="bookmarks">관심목록 <span id="saved-count">—</span></a></nav><div class="counts"><div>저장한 공고 <span id="job-count">—</span></div><div>저장한 교육 <span id="course-count">—</span></div></div><p class="side-note">내 프로필을 구체적으로 정리하고,<br>다음 준비에 활용해 보세요.</p><div class="back"><a class="button" href="/main">메인으로 돌아가기</a></div></aside>
<main class="content"><section class="panel" id="profile-overview" aria-labelledby="personal-title"><div class="section-anchor" tabindex="-1"></div><div class="section-head"><h2 id="personal-title">개인정보</h2><a class="button" href="/mypage/profile">정보 수정</a></div><dl class="info-grid"><div><dt>아이디 (이메일)</dt><dd>__EMAIL__</dd></div><div><dt>이름</dt><dd>__NAME__</dd></div><div><dt>비밀번호</dt><dd class="subtle">보안을 위해 표시하지 않습니다.</dd></div><div><dt>이메일 인증</dt><dd>인증 완료</dd></div></dl></section>
<section class="panel profile-information"><div class="section-head"><h2>프로필 정보</h2></div><p class="section-note">희망직무와 역량, 보유한 자격증과 이수한 교육을 추가하고 관리해 보세요.</p>
<div id="profile-data-content" class="loading"><div class="profile-item profile-item-editable"><details open><summary>희망직무 <span class="summary-note" id="roles-summary">불러오는 중…</span></summary><div class="entries"><div class="skills-tags" id="roles-list" aria-label="등록한 희망직무"></div><p class="skills-help" id="roles-empty">희망직무를 추가해 보세요.</p></div></details><button id="edit-role" type="button" class="button profile-edit-button" disabled>희망직무 수정</button></div>
<div class="profile-item profile-item-editable"><details open class="profile-skills"><summary>나의 역량 <span class="summary-note" id="skills-summary">불러오는 중…</span></summary><div class="entries">__SKILLS_CONTENT__</div></details><button id="edit-skills" type="button" class="button profile-edit-button" disabled>나의 역량 수정</button></div>
<details open><summary>자격증 <span class="summary-note" id="certificates-summary">불러오는 중…</span></summary><div class="entries" id="certificates-list"></div><button class="button add" data-add="certificates" disabled>+ 자격증 추가하기</button></details>
<details open><summary>교육이수 <span class="summary-note" id="courses-summary">불러오는 중…</span></summary><div class="entries" id="courses-list"></div><button class="button add" data-add="courses" disabled>+ 교육이수 추가하기</button></details>
</div>
<p id="profile-data-message" class="flash" role="status" aria-live="polite">프로필 정보를 불러오는 중이에요.</p><button id="retry" class="button hidden">다시 불러오기</button></section><section id="bookmarks" aria-labelledby="bookmarks-title"><h2 id="bookmarks-title" tabindex="-1">관심목록</h2><p class="section-note">저장한 채용공고와 교육과정을 한곳에서 확인하세요.</p>__BOOKMARKS_CONTENT__</section></main></div><p id="flash" class="flash" role="status" aria-live="polite"></p></div>
<footer>취준나침반 · 취업의 길, 한 번에 찾고, 한 걸음씩 함께 나아가요</footer>
<dialog id="editor" aria-labelledby="editor-title"><form id="editor-form"><h2 id="editor-title">프로필 정보 수정</h2><div id="editor-fields"></div><p id="editor-message" class="dialog-status" role="status" aria-live="polite"></p><div class="dialog-actions"><button type="button" class="button" id="cancel-editor">취소</button><button type="submit" class="button primary" id="save-editor">저장</button></div></form></dialog>
<script>
let profileData=null,editing=null,profileSkills=null;
const entryPath=kind=>'/api/mypage/'+(kind==='certificates'?'certifications':'trainings');
const byId=id=>document.getElementById(id),dialog=byId('editor'),saveButton=byId('save-editor');
async function api(url,options={}){const response=await fetch(url,options);if(response.status===401){location.assign('/signin');throw new Error('로그인이 필요합니다.');}if(response.status===204)return null;const data=await response.json();if(!response.ok)throw new Error(typeof data.detail==='string'?data.detail:'입력값을 확인해 주세요.');return data;}
function el(tag,text,className){const node=document.createElement(tag);node.textContent=text;if(className)node.className=className;return node;}
function message(text,error=false){byId('profile-data-message').textContent=text;byId('profile-data-message').className='flash '+(error?'error':'success');}
function render(){
 byId('target-role').textContent=profileData.target_role?profileData.target_role+' 직무 준비 중':'희망 직무를 입력해 보세요.';
 const roles=profileData.target_role.split(',').map(value=>value.trim()).filter(Boolean);
 byId('roles-list').replaceChildren(...roles.map(role=>{const tag=el('span','','skills-tag'),text=el('span','','skills-tag-text');text.append(el('span','#','skills-tag-hash'),document.createTextNode(role.replace(/^#+/,'').trim()));tag.append(text);return tag;}));
 byId('roles-summary').textContent=roles.length+'개 등록';byId('roles-empty').hidden=roles.length>0;
 for(const kind of ['certificates','courses']){const list=byId(kind+'-list');list.replaceChildren();byId(kind+'-summary').textContent=kind==='certificates'?profileData[kind].length+'개 보유':profileData[kind].length+'건 등록';if(!profileData[kind].length)list.append(el('p',kind==='certificates'?'등록한 자격증이 없어요. 보유한 자격증을 추가해 주세요.':'수료한 교육이 있다면 추가해 주세요.','empty'));
 profileData[kind].forEach((item,index)=>{const row=el('article','','entry'),copy=el('div',''),actions=el('div','','entry-actions');copy.append(el('h3',item.name),el('p',[item.organization,item.completed_on].filter(Boolean).join(' · ')));const edit=el('button','수정','button'),remove=el('button','삭제','button');edit.setAttribute('aria-label',item.name+' 수정');remove.setAttribute('aria-label',item.name+' 삭제');edit.onclick=()=>openEditor(kind,item.id);remove.onclick=async()=>{if(!confirm(item.name+' 항목을 삭제할까요?'))return;remove.disabled=true;try{await api(entryPath(kind)+'/'+encodeURIComponent(item.id),{method:'DELETE'});profileData[kind]=profileData[kind].filter(value=>value.id!==item.id);render();message('삭제했습니다.');}catch(error){message(error.message,true);}finally{remove.disabled=false;}};actions.append(edit,remove);row.append(copy,actions);list.append(row);});}
}
async function persist(next){profileData=await api('/api/mypage/profile',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({target_role:next.target_role})});render();}
async function load(){byId('retry').classList.add('hidden');message('프로필 정보를 불러오는 중이에요.');try{profileData=await api('/api/mypage/profile');render();byId('profile-data-content').classList.remove('loading');byId('edit-role').disabled=false;document.querySelectorAll('[data-add]').forEach(button=>button.disabled=false);message('프로필 정보를 추가하고 관리해 보세요.');}catch(error){message(error.message,true);byId('retry').classList.remove('hidden');}}
window.addEventListener('profile-skills-loaded',event=>{profileSkills=event.detail;byId('skills-summary').textContent=profileSkills.length+'개 등록';byId('edit-skills').disabled=false;});
function field(name,label,value='',type='text',required=false,max=100){const wrap=el('div','','field'),caption=el('label',label),input=document.createElement('input');caption.htmlFor='edit-'+name;input.id=caption.htmlFor;input.name=name;input.type=type;input.value=value||'';input.required=required;if(type==='text')input.maxLength=max;wrap.append(caption,input);byId('editor-fields').append(wrap);}
function isTagEditor(){return editing&&['role','skills'].includes(editing.kind);}
function checkTags(values){
 const role=editing.kind==='role',max=role?60:30,label=role?'희망직무':'역량',seen=new Set();
 if(values.length>20)throw new Error(label+(role?'는':'은')+' 최대 20개까지 등록할 수 있어요.');
 const checked=values.map(value=>{const tag=value.trim().replace(/^#+/,'').trim().replace(/\s+/g,' ');if(!tag||[...tag].length>max||/[\u0000-\u001f\u007f]/.test(tag))throw new Error(label+(role?'는':'은')+' 공백을 제외한 1~'+max+'자로 입력해 주세요.');const key=tag.toLocaleLowerCase();if(seen.has(key))throw new Error('이미 추가한 '+label+'입니다.');seen.add(key);return tag;});
 if(role&&checked.join(', ').length>1000)throw new Error('희망직무는 전체 1,000자 이내로 입력해 주세요.');
 return checked;
}
function renderDraftTags(){
 const list=byId('edit-tags');list.replaceChildren();
 editing.tags.forEach((value,index)=>{const tag=el('span','','skills-tag'),text=el('span','','skills-tag-text');text.append(el('span','#','skills-tag-hash'));text.append(document.createTextNode(value));const remove=el('button','×','skills-tag-remove');remove.type='button';remove.setAttribute('aria-label',value+' 삭제');remove.onclick=()=>{if(saveButton.disabled)return;editing.tags.splice(index,1);renderDraftTags();byId('edit-tag-input').focus();};tag.append(text,remove);list.append(tag);});
 byId('edit-tags-empty').hidden=editing.tags.length>0;
}
function addDraftTags(){
 if(saveButton.disabled)return false;
 const input=byId('edit-tag-input'),incoming=input.value.split(/[,，]/).map(value=>value.trim()).filter(Boolean);
 if(!incoming.length){byId('editor-message').textContent='추가할 내용을 입력해 주세요.';input.focus();return false;}
 try{editing.tags=checkTags([...editing.tags,...incoming]);input.value='';input.removeAttribute('aria-invalid');byId('editor-message').textContent='';renderDraftTags();return true;}catch(error){byId('editor-message').textContent=error.message;input.setAttribute('aria-invalid','true');input.focus();return false;}
}
function openEditor(kind,id=null){if(!profileData||(kind==='skills'&&profileSkills===null))return;editing={kind,id};byId('editor-fields').replaceChildren();byId('editor-message').textContent='';byId('editor-title').textContent=kind==='role'?'희망직무 수정':kind==='skills'?'나의 역량 수정':(kind==='certificates'?'자격증':'교육이수')+(id===null?' 추가':' 수정');
 if(isTagEditor()){
  const role=kind==='role',label=role?'희망직무':'역량';editing.tags=role?profileData.target_role.split(',').map(value=>value.trim()).filter(Boolean):[...profileSkills];
  const help=el('p',(role?'인사총무, 마케팅 등 희망직무를':'Python, SQL, 문제 해결 등 나의 역량을')+' 입력해 주세요. Enter 또는 쉼표로 추가할 수 있어요. 최대 20개, 각 '+(role?'60':'30')+'자까지 등록할 수 있습니다.','skills-help');help.id='edit-tags-help';
  const caption=el('label',label+' 추가');caption.htmlFor='edit-tag-input';const row=el('div','','skills-input-row'),input=document.createElement('input');input.id='edit-tag-input';input.type='text';input.autocomplete='off';input.placeholder=role?'예: 인사총무, 마케팅':'예: Python, SQL';input.setAttribute('aria-describedby','edit-tags-help editor-message');
  const add=el('button','추가','button');add.type='button';add.onclick=()=>{addDraftTags();input.focus();};row.append(input,add);const list=el('div','','skills-tags');list.id='edit-tags';const empty=el('p','등록한 '+label+(role?'가':'이')+' 없어요. '+label+(role?'를':'을')+' 추가해 보세요.','skills-help');empty.id='edit-tags-empty';byId('editor-fields').append(help,caption,row,list,empty);
  input.addEventListener('keydown',event=>{if(event.isComposing||event.keyCode===229)return;if(['Enter',',','，'].includes(event.key)){event.preventDefault();addDraftTags();}});renderDraftTags();
 }else{const item=id===null?{}:profileData[kind].find(value=>value.id===id);field('name',kind==='certificates'?'자격증명':'교육과정명',item.name,'text',true);field('organization',kind==='certificates'?'발급기관':'교육기관',item.organization);field('completed_on',kind==='certificates'?'취득일':'수료일',item.completed_on,'date');}
 dialog.showModal();if(isTagEditor())byId('edit-tag-input').focus();}
byId('editor-form').addEventListener('submit',async event=>{
 event.preventDefault();if(saveButton.disabled)return;
 if(isTagEditor()){if(byId('edit-tag-input').value.trim()&&!addDraftTags())return;try{editing.tags=checkTags(editing.tags);}catch(error){byId('editor-message').textContent=error.message;return;}}
 const values=Object.fromEntries(new FormData(event.target));for(const key in values)values[key]=values[key].trim();
 if('name'in values&&!values.name){byId('editor-message').textContent='이름을 입력해 주세요.';return;}
 const {kind,id}=editing;
 saveButton.disabled=true;byId('cancel-editor').disabled=true;byId('editor-message').textContent='저장 중…';
 try{
  if(kind==='role'){await persist({target_role:editing.tags.join(', ')});}
  else if(kind==='skills'){const saved=await api('/api/mypage/skills',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({skills:editing.tags})});profileSkills=saved.skills;byId('skills-summary').textContent=profileSkills.length+'개 등록';window.dispatchEvent(new CustomEvent('profile-skills-saved',{detail:profileSkills}));}
  else{
   values.completed_on=values.completed_on||null;
   const saved=await api(entryPath(kind)+(id===null?'':'/'+encodeURIComponent(id)),{method:id===null?'POST':'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify(values)});
   if(id===null)profileData[kind].push(saved);else profileData[kind]=profileData[kind].map(value=>value.id===id?saved:value);
   render();
  }
  dialog.close();message('변경 내용을 저장했습니다.');
 }catch(error){byId('editor-message').textContent=error.message;}
 finally{saveButton.disabled=false;byId('cancel-editor').disabled=false;}
});

dialog.addEventListener('cancel',event=>{if(saveButton.disabled)event.preventDefault();});byId('cancel-editor').onclick=()=>dialog.close();byId('edit-role').onclick=()=>openEditor('role');byId('edit-skills').onclick=()=>openEditor('skills');document.querySelectorAll('[data-add]').forEach(button=>button.onclick=()=>openEditor(button.dataset.add));byId('retry').onclick=load;

window.addEventListener('bookmarks-loaded',event=>{const counts=event.detail;byId('saved-count').textContent=counts.all;byId('job-count').textContent=counts.job;byId('course-count').textContent=counts.course;});load();
const sectionLinks=[...document.querySelectorAll('[data-section]')];
function selectSection(id){for(const link of sectionLinks){const active=link.dataset.section===id;link.classList.toggle('active',active);if(active)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current');}}
function updateSection(){const rect=byId('bookmarks').getBoundingClientRect();const mobile=matchMedia('(max-width:800px)').matches;const marker=mobile?document.querySelector('.sidebar').getBoundingClientRect().height+32:Math.min(innerHeight*.35,220);const atEnd=scrollY+innerHeight>=document.documentElement.scrollHeight-3;selectSection(rect.top<=marker||(atEnd&&rect.top<innerHeight)?'bookmarks':'profile-overview');}
let scrollPending=false;
function scheduleSection(){if(scrollPending)return;scrollPending=true;requestAnimationFrame(()=>{scrollPending=false;updateSection();});}
sectionLinks.forEach(link=>link.addEventListener('click',event=>{event.preventDefault();const target=byId(link.dataset.section);history.pushState(null,'',link.getAttribute('href'));target.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'instant':'smooth',block:'start'});const focus=target.querySelector('[tabindex="-1"]')||target.querySelector('h2');focus.focus({preventScroll:true});scheduleSection();}));
window.addEventListener('scroll',scheduleSection,{passive:true});window.addEventListener('resize',scheduleSection);window.addEventListener('hashchange',scheduleSection);new ResizeObserver(scheduleSection).observe(document.querySelector('.content'));updateSection();
__BOOKMARKS_SCRIPT__
</script>__CC_SCRIPT____SKILLS_SCRIPT__
</body></html>'''
