
"use strict";
const rEl=id=>document.getElementById(id);
const rEsc=value=>String(value??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const rState={jobId:null,result:null,roleResult:null,saved:[],controller:null,visibleCourseCount:3,aiBusy:false,activeAction:null,skillSignature:null,availableSkills:[],selectedSkills:[],excludedCompanyNames:[]};
const rMode=value=>({online:"온라인",offline:"오프라인",mixed:"혼합"}[value]||"방식 원문 확인");
const rCost=value=>value==null?"교육비 원문 확인":value===0?"무료":value.toLocaleString("ko-KR")+"원";
function safeCourseUrl(value){try{const u=new URL(value);return ["https:","http:"].includes(u.protocol)&&["www.work24.go.kr","work24.go.kr","hrd.work24.go.kr","www.hrd.go.kr"].includes(u.hostname)&&!u.username&&!u.password?u.href:"";}catch{return "";}}
try{const keys=JSON.parse(localStorage.getItem("training-collection-favorites")||"[]");if(Array.isArray(keys))rState.saved=keys.filter(k=>typeof k==="string");}catch{}
let rToastTimer;
function rToast(message){rEl("aiToast").textContent=message;rEl("aiToast").classList.add("show");clearTimeout(rToastTimer);rToastTimer=setTimeout(()=>rEl("aiToast").classList.remove("show"),2800);}
Object.assign(rState,{mode:'all',expanded:false,jobs:[],revision:0,requestedSkills:[]});
function showEmpty(message){rEl("recommendCards").innerHTML='<p class="rec-empty">'+rEsc(message)+'</p>';}
function renderRecommendations(){
  const data=rState.result;if(!data)return;
  const allItems=data.items.slice(0,15);
  const items=allItems.slice(0,rState.visibleCourseCount);
  rEl("courseMore").hidden=allItems.length<=3;
  rEl("courseMore").textContent=rState.visibleCourseCount>3?"3개만 보기":rState.activeAction?"추천 교육 더 보기":"직무 관련 교육 더 보기";
  rEl("courseMore").setAttribute("aria-expanded",String(rState.visibleCourseCount>3));
  const isAi=["groq","gemini"].includes(data.meta.source);
  updateActionButtons();
  rEl("recommendTitle").textContent=isAi?(rState.activeAction==='selected'?'선택한 역량 기준 AI 추천':'전체 보완역량 기준 AI 추천'):"AI 가 추천하는 직무 관련 교육";
  rEl("recommendCriteria").textContent=isAi?'추천 기준: '+rState.requestedSkills.join(' · '):(data.job.job_name||data.roles.join(' · ')||'선택한 공고 직무')+' 직무를 기준으로 먼저 모은 교육이에요.';
  if(!items.length){showEmpty(isAi?"전체 부족 역량과 연결되는 교육을 찾지 못했어요.":data.roles.length?"선택한 직무와 연관된 교육이 없습니다. 다른 공고를 선택하거나 교육모음에서 검색해 주세요.":"선택한 공고의 직무에 해당하는 교육 분류가 없습니다. 교육모음에서 원하는 교육을 검색해 주세요.");return;}
  rEl("recommendCards").innerHTML=items.map((c,i)=>{
    const saved=rState.saved.includes(c.key);
    return '<article class="rec-card"><div class="rec-card-top"><span class="rec-rank">'+String(i+1).padStart(2,"0")+'</span><button type="button" class="heart" data-course-save="'+rEsc(c.key)+'" aria-label="'+rEsc(c.title)+' 관심 '+(saved?'해제':'저장')+'" aria-pressed="'+saved+'">'+(saved?'♥':'♡')+'</button></div><h3 title="'+rEsc(c.title)+'">'+rEsc(c.title)+'</h3><p class="provider">'+rEsc(c.provider)+'</p><span class="learning-badge">'+rEsc(c.skill_label)+'</span><div class="rec-explanation"><strong class="reason-label">'+(isAi?'AI 추천 이유':'직무 관련 정보')+'</strong><p class="rec-reason" title="'+rEsc(c.reason)+'">'+rEsc(c.reason)+'</p></div><p class="rec-meta">'+rEsc(rCost(c.cost))+' · '+rEsc(rMode(c.mode))+'</p><button type="button" class="rec-detail" data-course-detail="'+rEsc(c.key)+'">교육 상세 / 원문 보기 →</button></article>';
  }).join("");
}
function showRecommendedDetail(c){
  const isAi=["groq","gemini"].includes(rState.result?.meta.source);
  const fields=[["교육기관",c.provider],["기간",(c.start||"미정")+" ~ "+(c.end||"미정")],["교육비",rCost(c.cost)],["교육 방식",rMode(c.mode)],[isAi?"학습 목표":"관련 직무",isAi?c.skill_label:c.related_roles.join(" · ")],[isAi?"AI 추천 이유":"직무 관련 정보",c.reason]];
  const url=safeCourseUrl(c.url);
  rEl("recommendDetailBody").innerHTML='<h2 class="modal-title" id="recommendDetailTitle">'+rEsc(c.title)+'</h2><dl class="detail-grid">'+fields.map(([label,value])=>'<dt>'+rEsc(label)+'</dt><dd>'+rEsc(value)+'</dd>').join("")+'</dl><p class="detail-note">교육의 지원 자격·본인부담금과 최신 일정은 고용24 원문에서 확인해 주세요.</p>'+(url?'<a class="primary-link" href="'+rEsc(url)+'" target="_blank" rel="noopener noreferrer">고용24 원문 보기 ↗</a>':'');
  rEl("recommendDetailDialog").showModal();
}

function analyzedJobs(){
  const jobs=[];
  try{for(const key of Object.keys(localStorage)){
    const id=key.startsWith('jd-match-score:v2:')?key.slice('jd-match-score:v2:'.length):'';
    if(!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id))continue;
    try{const cached=JSON.parse(localStorage.getItem(key)),score=cached?.score||cached;
      if(Array.isArray(score?.missing_skills))jobs.push({id,savedAt:Number(cached?.savedAt)||0,score});
    }catch{}
  }}catch{}
  return jobs.sort((a,b)=>b.savedAt-a.savedAt).slice(0,5);
}
function readAnalyzedSkills(){
  const entry=rState.jobs.find(job=>job.id===rState.jobId),skills=[];
  for(const value of entry?.score.missing_skills||[]){
    if(typeof value!=='string')continue;const skill=value.trim();
    if(skill&&!rState.excludedCompanyNames.includes(skill)&&!skills.some(item=>item.toLocaleLowerCase()===skill.toLocaleLowerCase()))skills.push(skill);
  }
  rState.availableSkills=skills;
  rState.selectedSkills=rState.selectedSkills.filter(skill=>skills.includes(skill));
  return {hasAnalysis:!!entry,skills};
}
function fitSkillRow(){
  const box=rEl('gapPills'),chips=[...box.children],button=rEl('gapMore');
  box.dataset.expanded=String(rState.expanded);
  chips.forEach(chip=>chip.hidden=false);
  button.setAttribute('aria-expanded',String(rState.expanded));
  if(!chips.length||!rState.availableSkills.length){button.hidden=true;return;}
  if(rState.expanded){button.hidden=false;button.textContent='간단히 보기 ↑';return;}
  const firstTop=chips[0].offsetTop,firstRow=chips.filter(chip=>Math.abs(chip.offsetTop-firstTop)<2).length;
  chips.forEach((chip,i)=>chip.hidden=i>=firstRow);
  const remaining=chips.length-firstRow;button.hidden=remaining===0;button.textContent='나머지 '+remaining+'개 · 전체 보기 ↓';
}
function updateActionButtons(){
  const button=rEl('aiCourseList'),selected=rState.mode==='selected';
  button.disabled=rState.aiBusy||!rState.jobId||!(selected?rState.selectedSkills.length:rState.availableSkills.length);
  button.textContent=rState.aiBusy?'맞춤 교육을 찾고 있어요…':selected?'선택한 '+rState.selectedSkills.length+'개 역량으로 AI 추천받기':'전체 '+rState.availableSkills.length+'개 역량으로 AI 추천받기';
  rEl('returnRoleCourses').hidden=!rState.activeAction;
  rEl('returnRoleCourses').disabled=rState.aiBusy;
  rEl('selectedKeywordCount').textContent=selected?'선택한 역량 '+rState.selectedSkills.length+'개':'보완역량 '+rState.availableSkills.length+'개 전체 기준';
  document.querySelectorAll('input[name="recommendMode"]').forEach(input=>input.disabled=rState.aiBusy);
}
function renderSkillSelection(){
  const box=rEl('gapPills'),selected=rState.mode==='selected';box.replaceChildren();
  for(const skill of rState.availableSkills){
    const chip=document.createElement(selected?'button':'span');chip.className='gap-pill';chip.textContent=skill;chip.title=skill;
    if(selected){chip.type='button';chip.dataset.recommendSkill=skill;chip.setAttribute('aria-pressed',String(rState.selectedSkills.includes(skill)));chip.disabled=rState.aiBusy;}
    box.append(chip);
  }
  rEl('skillRecommendationStatus').textContent=!rState.availableSkills.length?'현재 분석에서 확인된 보완역량이 없습니다. 직무 관련 교육을 살펴보세요.':selected?'추천받고 싶은 역량만 선택하세요. 목록을 접어도 선택은 유지돼요.':'목록이 접혀 있어도 '+rState.availableSkills.length+'개 역량을 모두 추천에 반영해요.';
  updateActionButtons();fitSkillRow();
}
async function loadCourses(){
  rState.controller?.abort();const id=rState.jobId;if(!id)return;
  const controller=new AbortController();rState.controller=controller;
  rEl('courseMore').hidden=true;rEl('recommendCards').setAttribute('aria-busy','true');
  rEl('recommendTitle').textContent='AI 가 추천하는 직무 관련 교육';
  rEl('recommendCriteria').textContent='선택한 공고의 직무와 관련된 교육을 불러오고 있어요.';
  showEmpty('직무와 관련된 교육을 불러오고 있어요.');
  try{
    const response=await fetch('/training_match/api/recommendations',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({job_id:id}),cache:'no-store',signal:controller.signal});
    if(response.status===401){location.assign('/signin');return;}
    const data=await response.json();if(!response.ok)throw new Error(data.error||'교육을 불러오지 못했습니다.');
    if(controller.signal.aborted||id!==rState.jobId)return;
    rState.roleResult=data;rState.result=data;renderRecommendations();
    rEl('recommendSource').textContent='고용24 저장 자료 · '+data.meta.fetchedAt+' 조회';
  }catch(error){if(error.name!=='AbortError'&&id===rState.jobId)showEmpty((error.message||'교육을 불러오지 못했어요.')+' 공고를 다시 선택해 재시도해 주세요.');}
  finally{if(rState.controller===controller){rState.controller=null;rEl('recommendCards').setAttribute('aria-busy','false');}}
}
async function chooseJob(id,scroll=true){
  rState.revision++;rState.controller?.abort();
  rState.jobId=rState.jobs.some(job=>job.id===id)?id:null;
  Object.assign(rState,{result:null,roleResult:null,selectedSkills:[],excludedCompanyNames:[],visibleCourseCount:3,mode:'all',expanded:false,activeAction:null,aiBusy:false,requestedSkills:[]});
  document.querySelectorAll('input[name="recommendMode"]').forEach(input=>input.checked=input.value==='all');
  rEl('educationContent').hidden=!rState.jobId;rEl('selectJobPrompt').hidden=!!rState.jobId;
  rEl('aiRecommendationStatus').hidden=true;rEl('recommendDetailDialog').close();
  rEl('recommendSource').textContent='직무 기반 교육추천 · 고용24 교육 정보';
  const url=new URL(location.href);if(rState.jobId)url.searchParams.set('job_id',rState.jobId);else url.searchParams.delete('job_id');history.replaceState(null,'',url.pathname+url.search);
  readAnalyzedSkills();renderSkillSelection();
  if(!rState.jobId)return;
  const entry=rState.jobs.find(job=>job.id===rState.jobId);
  rEl('selectedJobSummary').textContent='선택한 공고: '+entry.label+' · 보완역량 '+rState.availableSkills.length+'개';
  if(scroll)requestAnimationFrame(()=>requestAnimationFrame(()=>rEl('recommendStep').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'})));
  await loadCourses();
}
async function initJobs(){
  const select=rEl('analyzedJob'),status=rEl('jobSelectionStatus');select.disabled=true;rEl('retryJobs').hidden=true;
  rState.jobs=analyzedJobs();
  if(!rState.jobs.length){select.replaceChildren(new Option('저장된 분석 결과가 없습니다.',''));status.textContent='적합도 분석을 먼저 진행하면 여기서 공고를 선택할 수 있어요.';return;}
  status.textContent='분석한 공고 정보를 불러오는 중이에요.';
  let failures=0;
  await Promise.all(rState.jobs.map(async entry=>{
    try{const response=await fetch('/jd_match/job-postings/'+encodeURIComponent(entry.id),{cache:'no-store'});if(!response.ok)throw new Error();const job=await response.json();entry.label=job.company_name+' · '+job.title;}
    catch{failures++;entry.label='분석 공고 '+entry.id.slice(0,8)+' · 상세 정보 확인 필요';}
  }));
  select.replaceChildren(new Option('공고를 선택해 주세요.',''));
  for(const entry of rState.jobs){const date=entry.savedAt?new Date(entry.savedAt).toLocaleDateString('ko-KR'):'';select.add(new Option(entry.label+(date?' · '+date+' 분석':''),entry.id));}
  select.disabled=false;status.textContent=failures?'일부 공고명을 불러오지 못했습니다. 공고 정보를 다시 불러오거나 다른 공고를 선택해 주세요.':'';rEl('retryJobs').hidden=!failures;
  const requested=new URLSearchParams(location.search).get('job_id');
  if(requested&&rState.jobs.some(job=>job.id===requested)){select.value=requested;await chooseJob(requested,false);}
  else if(requested)status.textContent='이 공고의 분석 결과가 현재 브라우저에 없습니다. 저장된 공고를 선택하거나 다시 적합도 분석을 진행해 주세요.';
}
async function recommendAllSkills(){
  if(rState.aiBusy||!rState.jobId)return;
  const analyzed=readAnalyzedSkills(),selectedOnly=rState.mode==='selected';
  const skills=selectedOnly?[...rState.selectedSkills]:analyzed.skills;
  if(!skills.length)return;
  const revision=rState.revision,previous=rState.roleResult||rState.result;
  rState.controller?.abort();rState.controller=null;
  const controller=new AbortController();rState.aiController?.abort();rState.aiController=controller;
  rState.aiBusy=true;renderSkillSelection();
  const status=rEl('aiRecommendationStatus'),target=selectedOnly?'선택한 역량':'전체 보완역량';status.hidden=false;status.textContent=target+'에 맞는 교육을 AI가 찾고 있어요.';
  rEl('recommendCards').setAttribute('aria-busy','true');
  try{
    const response=await fetch('/training_match/api/skill-recommendations',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({missing_skills:skills}),cache:'no-store',signal:controller.signal});
    if(revision!==rState.revision||controller.signal.aborted)return;
    if(response.status===401){location.assign('/signin');return;}
    const data=await response.json();if(!response.ok)throw new Error(data.error||'AI 교육 추천을 완료하지 못했어요. 다시 시도해 주세요.');
    if(revision!==rState.revision||controller.signal.aborted)return;
    rState.excludedCompanyNames=[...new Set([...rState.excludedCompanyNames,...(data.excluded_company_names||[])])];readAnalyzedSkills();
    rState.requestedSkills=skills.filter(skill=>!rState.excludedCompanyNames.includes(skill));
    rState.result={...data,job:previous?.job||{job_name:''},roles:previous?.roles||[],meta:{...data.meta,source:data.meta.source||'gemini'},items:data.items.map(c=>({...c,reason:c.ai_reason}))};
    rState.activeAction=selectedOnly?'selected':'all';rState.visibleCourseCount=3;renderRecommendations();
    status.textContent=data.items.length?target+'에 맞는 교육 '+data.items.length+'개를 추천했어요.':'보완역량과 관련된 교육을 찾지 못했어요.';
    rEl('recommendSource').textContent='고용24 저장 자료 · '+data.meta.fetchedAt+' · '+data.meta.model;
  }catch(error){if(error.name!=='AbortError'&&revision===rState.revision)status.textContent=error.message||'AI 교육 추천에 실패했습니다. 다시 시도해 주세요.';}
  finally{if(revision===rState.revision){rState.aiBusy=false;rState.aiController=null;rEl('recommendCards').setAttribute('aria-busy','false');renderSkillSelection();}}
}
document.querySelectorAll('input[name="recommendMode"]').forEach(input=>input.addEventListener('change',()=>{rState.mode=input.value;rState.expanded=false;renderSkillSelection();}));
rEl('gapMore').addEventListener('click',()=>{rState.expanded=!rState.expanded;fitSkillRow();});
rEl('gapPills').addEventListener('click',event=>{
  const button=event.target.closest('[data-recommend-skill]');if(!button||rState.aiBusy)return;
  const skill=button.dataset.recommendSkill;
  rState.selectedSkills=rState.selectedSkills.includes(skill)?rState.selectedSkills.filter(item=>item!==skill):[...rState.selectedSkills,skill];
  button.setAttribute('aria-pressed',String(rState.selectedSkills.includes(skill)));updateActionButtons();
});
rEl('analyzedJob').addEventListener('change',()=>{rState.aiController?.abort();chooseJob(rEl('analyzedJob').value);});
rEl('retryJobs').addEventListener('click',()=>initJobs());
rEl('aiCourseList').addEventListener('click',recommendAllSkills);
rEl('returnRoleCourses').addEventListener('click',()=>{
  if(rState.aiBusy)return;rState.activeAction=null;rEl('aiRecommendationStatus').hidden=true;updateActionButtons();
  if(!rState.roleResult){loadCourses();return;}rState.result=rState.roleResult;rState.visibleCourseCount=3;renderRecommendations();
  rEl('recommendSource').textContent='고용24 저장 자료 · '+rState.roleResult.meta.fetchedAt+' 조회';
});
rEl('courseMore').addEventListener('click',()=>{if(rState.result){rState.visibleCourseCount=rState.visibleCourseCount>3?3:15;renderRecommendations();}});
rEl('recommendDetailClose').addEventListener('click',()=>rEl('recommendDetailDialog').close());
rEl('recommendCards').addEventListener('click',event=>{
  const save=event.target.closest('[data-course-save]'),detail=event.target.closest('[data-course-detail]');
  if(save){const key=save.dataset.courseSave;rState.saved=rState.saved.includes(key)?rState.saved.filter(k=>k!==key):[...rState.saved,key];try{localStorage.setItem('training-collection-favorites',JSON.stringify(rState.saved));rToast('관심목록을 변경했어요.');}catch{rToast('이번 화면에서만 관심 정보가 유지돼요.');}renderRecommendations();}
  if(detail){const course=rState.result?.items.find(c=>c.key===detail.dataset.courseDetail);if(course)showRecommendedDetail(course);}
});
let skillWidth=-1;
if(typeof ResizeObserver!=='undefined')new ResizeObserver(entries=>{const width=entries[0].contentRect.width;if(Math.abs(width-skillWidth)>.5){skillWidth=width;fitSkillRow();}}).observe(rEl('gapPills'));
document.fonts.ready.then(fitSkillRow);
window.CompassLoading.track(initJobs());
