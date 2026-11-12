// 공고모음과 메인에서 함께 사용하는 카드·북마크 동작.
(()=>{
  'use strict';
  function element(tag,text,className){const node=document.createElement(tag);if(text!==undefined&&text!==null)node.textContent=text;if(className)node.className=className;return node;}
  async function api(url,options={}){
    const response=await fetch(url,{credentials:'same-origin',cache:'no-store',...options});
    if(response.status===401){location.replace('/signin');throw new Error('로그인이 만료되었습니다. 다시 로그인해 주세요.');}
    let data=null;if(response.status!==204){try{data=await response.json();}catch{}}
    if(!response.ok){const detail=data?.detail;const error=new Error(typeof detail==='string'?detail:detail?.message||'요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.');error.status=response.status;error.code=detail?.code;throw error;}
    return data;
  }
  function createRenderer({list,onError=()=>{},onNotice=()=>{}}){
    const busyHearts=new Set();
  function careerLabel(job){
    const type=job.career_type||'경력 확인';if(type==='신입'||type==='무관')return type==='무관'?'경력 무관':type;
    const lower=job.min_experience_years,upper=job.max_experience_years;
    if(lower!==null&&upper!==null)return type+' '+lower+'–'+upper+'년';
    if(lower!==null&&lower>0)return type+' '+lower+'년 이상';
    return type;
  }
  function dueLabel(job){if(job.deadline_date)return '마감 '+job.deadline_date.replaceAll('-','.');return ['상시','채용 시'].includes(job.deadline_type)?job.deadline_type+' 채용':'마감일 원문 확인';}
  function wantedUrl(value){try{const url=new URL(value);if(url.protocol==='https:'&&['www.wanted.co.kr','wanted.co.kr'].includes(url.hostname)&&!url.username&&!url.password&&/^\/wd\/\d+\/?$/.test(url.pathname))return url.href;}catch{}return null;}
  function heartState(button,saved){button.setAttribute('aria-pressed',String(saved));button.setAttribute('aria-label',button.dataset.title+(saved?' 관심 공고 저장 취소':' 관심 공고 저장'));button.title=saved?'저장 취소':'관심 공고 저장';}
  async function toggleBookmark(button,job){
    if(busyHearts.has(job.id))return;
    const saved=button.getAttribute('aria-pressed')==='true';busyHearts.add(job.id);button.disabled=true;onError('');
    try{
      try{
        await api(saved?'/api/bookmarks/job:'+encodeURIComponent(job.id):'/api/bookmarks',saved?{method:'DELETE'}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({item_type:'job',source_id:job.id})});
      }catch(error){if(!(saved&&error.status===404)&&!(!saved&&error.status===409&&error.code==='BOOKMARK_ALREADY_EXISTS'))throw error;}
      for(const current of list.querySelectorAll('.heart-button'))if(current.dataset.id===job.id)heartState(current,!saved);
      window.dispatchEvent(new Event('job-bookmark-changed'));
      onNotice(saved?'관심 공고에서 삭제했어요.':'관심 공고에 저장했어요.');
    }catch(error){onError(error.message);onNotice('저장 상태를 변경하지 못했어요.');}
    finally{busyHearts.delete(job.id);for(const current of list.querySelectorAll('.heart-button'))if(current.dataset.id===job.id)current.disabled=false;}
  }
  function card(job){
    const group=element('div',null,'job-card-group'),article=element('article',null,'job-card');
    const url=wantedUrl(job.source_url);const link=element(url?'a':'div',null,'card-main-link');
    if(url){link.href=url;link.target='_blank';link.rel='noopener noreferrer';link.setAttribute('aria-label',job.title+' · 원티드 원문 새 탭에서 보기');}
    const top=element('div',null,'card-top');top.append(element('span',job.use_yn==='N'?'채용 마감':'채용 중','status-badge'+(job.use_yn==='N'?' closed':'')));
    link.append(top,element('p',job.company_name,'company-name'),element('h3',job.title,'job-title'),element('span',job.job_name,'job-role'));
    const meta=element('p',null,'job-meta');for(const text of [job.region_name,careerLabel(job),job.employment_type||'고용형태 확인'])meta.append(element('span',text));link.append(meta);
    const footer=element('div',null,'card-footer');footer.append(element('span',dueLabel(job)),element('span',url?'상세 보기  →':'원문 주소 확인 필요','card-detail'));link.append(footer);
    const heart=element('button',null,'heart-button');heart.type='button';heart.dataset.id=job.id;heart.dataset.title=job.title;heart.disabled=busyHearts.has(job.id);heartState(heart,job.is_saved);
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('aria-hidden','true');const path=document.createElementNS('http://www.w3.org/2000/svg','path');path.setAttribute('d','M20.5 5.7c-2-2.1-5.2-1.4-6.7.4L12 8.2l-1.8-2.1c-1.5-1.8-4.7-2.5-6.7-.4C.2 9.2 3.7 13.8 12 21c8.3-7.2 11.8-11.8 8.5-15.3Z');svg.append(path);heart.append(svg);heart.addEventListener('click',()=>toggleBookmark(heart,job));article.append(link,heart);
    const compare=element('a','내 이력과 비교하기  ↗','comparison-link');compare.href='/jd_match/'+encodeURIComponent(job.id);group.append(article,compare);return group;
  }
    return {card};
  }
  window.CompassJobCards={element,api,createRenderer};
})();
