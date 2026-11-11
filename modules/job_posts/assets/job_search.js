(()=>{
  'use strict';
  const $=id=>document.getElementById(id);
  const form=$('filter-form'), keyword=$('keyword'), list=$('job-list'), pages=$('pagination');
  const defaults={q:'',job:'',region:'',career:'',employment:'',exclude_closed:true,sort:'default',page:1,size:8};
  const selects={job:$('job-filter'),region:$('region-filter'),career:$('career-filter'),employment:$('employment-filter')};
  let state={...defaults}, controller=null, sequence=0, toastTimer=null;
  const busyHearts=new Set();
  const urlParams=new URLSearchParams(location.search);
  for(const key of ['q','job','region','career','employment'])state[key]=urlParams.get(key)||'';
  state.sort=['default','deadline','company'].includes(urlParams.get('sort'))?urlParams.get('sort'):'default';
  state.exclude_closed=urlParams.get('exclude_closed')!=='false';
  state.page=Math.max(1,Math.min(10000,Number.parseInt(urlParams.get('page'),10)||1));
  function element(tag,text,className){const node=document.createElement(tag);if(text!==undefined&&text!==null)node.textContent=text;if(className)node.className=className;return node;}
  function params(){const query=new URLSearchParams();for(const [key,value] of Object.entries(state)){if(value!==''&&value!==defaults[key])query.set(key,String(value));}return query;}
  function syncUrl(){const query=params().toString();history.replaceState(null,'',location.pathname+(query?'?'+query:''));}
  function fillControls(){keyword.value=state.q;for(const [key,select] of Object.entries(selects))select.value=state[key];$('exclude-closed').checked=state.exclude_closed;$('sort-order').value=state.sort;}
  function readControls(){const next={...state,q:keyword.value.trim(),sort:$('sort-order').value,exclude_closed:$('exclude-closed').checked,page:1};for(const [key,select] of Object.entries(selects))next[key]=select.value;return next;}
  function toast(message){$('bookmark-toast').textContent=message;$('bookmark-toast').hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('bookmark-toast').hidden=true,3000);}
  async function api(url,options={}){
    const response=await fetch(url,{credentials:'same-origin',cache:'no-store',...options});
    if(response.status===401){location.replace('/signin');throw new Error('로그인이 만료되었습니다. 다시 로그인해 주세요.');}
    let data=null;if(response.status!==204){try{data=await response.json();}catch{}}
    if(!response.ok){const detail=data?.detail;const error=new Error(typeof detail==='string'?detail:detail?.message||'요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.');error.status=response.status;error.code=detail?.code;throw error;}
    return data;
  }
  function showState(title,description,failed=false){list.replaceChildren();pages.replaceChildren();$('results-state').hidden=false;$('state-title').textContent=title;$('state-description').textContent=description;$('retry-search').hidden=!failed;$('clear-search').hidden=failed;}
  function skeleton(){list.replaceChildren();for(let i=0;i<8;i++){const box=element('div',null,'skeleton');box.setAttribute('aria-hidden','true');for(let k=0;k<4;k++)box.append(element('span'));list.append(box);}}
  function chips(){
    const box=$('active-filters');box.replaceChildren();
    for(const key of ['q','job','region','career','employment']){
      if(!state[key])continue;
      const label=key==='q'?'“'+state[key]+'”':selects[key].selectedOptions[0]?.textContent||state[key];
      const button=element('button',null,'filter-chip');button.type='button';button.setAttribute('aria-label',label+' 조건 해제');button.append(element('span',label),element('span','×'));
      button.addEventListener('click',()=>{state[key]='';state.page=1;fillControls();loadJobs();});box.append(button);
    }
  }
  function careerLabel(job){
    const type=job.career_type||'경력 확인';if(type==='신입'||type==='무관')return type==='무관'?'경력 무관':type;
    const lower=job.min_experience_years,upper=job.max_experience_years;
    if(lower!==null&&upper!==null)return type+' '+lower+'–'+upper+'년';
    if(lower!==null&&lower>0)return type+' '+lower+'년 이상';
    return type;
  }
  function dueLabel(job){if(job.is_closed)return '마감 '+job.deadline_date.replaceAll('-','.');if(job.deadline_date)return '마감 '+job.deadline_date.replaceAll('-','.');return ['상시','채용 시'].includes(job.deadline_type)?job.deadline_type+' 채용':'마감일 원문 확인';}
  function wantedUrl(value){try{const url=new URL(value);if(url.protocol==='https:'&&['www.wanted.co.kr','wanted.co.kr'].includes(url.hostname)&&!url.username&&!url.password&&/^\/wd\/\d+\/?$/.test(url.pathname))return url.href;}catch{}return null;}
  function heartState(button,saved){button.setAttribute('aria-pressed',String(saved));button.setAttribute('aria-label',button.dataset.title+(saved?' 관심 공고 저장 취소':' 관심 공고 저장'));button.title=saved?'저장 취소':'관심 공고 저장';}
  async function toggleBookmark(button,job){
    if(busyHearts.has(job.id))return;
    const saved=button.getAttribute('aria-pressed')==='true';busyHearts.add(job.id);button.disabled=true;$('inline-status').textContent='';
    try{
      try{
        await api(saved?'/api/bookmarks/job:'+encodeURIComponent(job.id):'/api/bookmarks',saved?{method:'DELETE'}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({item_type:'job',source_id:job.id})});
      }catch(error){if(!(saved&&error.status===404)&&!(!saved&&error.status===409&&error.code==='BOOKMARK_ALREADY_EXISTS'))throw error;}
      for(const current of list.querySelectorAll('.heart-button'))if(current.dataset.id===job.id)heartState(current,!saved);
      toast(saved?'관심 공고에서 삭제했어요.':'관심 공고에 저장했어요.');
    }catch(error){$('inline-status').textContent=error.message;toast('저장 상태를 변경하지 못했어요.');}
    finally{busyHearts.delete(job.id);for(const current of list.querySelectorAll('.heart-button'))if(current.dataset.id===job.id)current.disabled=false;}
  }
  function card(job){
    const group=element('div',null,'job-card-group'),article=element('article',null,'job-card');
    const url=wantedUrl(job.source_url);const link=element(url?'a':'div',null,'card-main-link');
    if(url){link.href=url;link.target='_blank';link.rel='noopener noreferrer';link.setAttribute('aria-label',job.title+' · 원티드 원문 새 탭에서 보기');}
    const top=element('div',null,'card-top');top.append(element('span',job.is_closed?'마감':'채용 중','status-badge'+(job.is_closed?' closed':'')));
    link.append(top,element('p',job.company_name,'company-name'),element('h3',job.title,'job-title'),element('span',job.job_name,'job-role'));
    const meta=element('p',null,'job-meta');for(const text of [job.region_name,careerLabel(job),job.employment_type||'고용형태 확인'])meta.append(element('span',text));link.append(meta);
    const footer=element('div',null,'card-footer');footer.append(element('span',dueLabel(job)),element('span',url?'상세 보기  →':'원문 주소 확인 필요','card-detail'));link.append(footer);
    const heart=element('button',null,'heart-button');heart.type='button';heart.dataset.id=job.id;heart.dataset.title=job.title;heart.disabled=busyHearts.has(job.id);heartState(heart,job.is_saved);
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 24 24');svg.setAttribute('aria-hidden','true');const path=document.createElementNS('http://www.w3.org/2000/svg','path');path.setAttribute('d','M20.5 5.7c-2-2.1-5.2-1.4-6.7.4L12 8.2l-1.8-2.1c-1.5-1.8-4.7-2.5-6.7-.4C.2 9.2 3.7 13.8 12 21c8.3-7.2 11.8-11.8 8.5-15.3Z');svg.append(path);heart.append(svg);heart.addEventListener('click',()=>toggleBookmark(heart,job));article.append(link,heart);
    const compare=element('a','내 이력과 비교하기  ↗','comparison-link');compare.href='/jd_match/'+encodeURIComponent(job.id);group.append(article,compare);return group;
  }
  function paginate(total){
    pages.replaceChildren();const count=Math.ceil(total/state.size);if(count<=1)return;
    function button(label,page,current=false){const node=element('button',label);node.type='button';node.disabled=page<1||page>count;if(current)node.setAttribute('aria-current','page');node.setAttribute('aria-label',typeof label==='number'?label+'페이지':label+' 페이지');node.addEventListener('click',()=>{state.page=page;loadJobs(true);});pages.append(node);}
    button('이전',state.page-1);let start=Math.max(1,state.page-2);start=Math.min(start,Math.max(1,count-4));for(let i=start;i<=Math.min(count,start+4);i++)button(i,i,i===state.page);button('다음',state.page+1);
  }
  async function loadJobs(scroll=false){
    const run=++sequence;controller?.abort();controller=new AbortController();syncUrl();chips();$('inline-status').textContent='';$('results-state').hidden=true;list.setAttribute('aria-busy','true');pages.replaceChildren();skeleton();$('results-heading').textContent='공고를 찾고 있어요';
    try{
      const query=new URLSearchParams({...state,size:String(state.size),page:String(state.page),exclude_closed:String(state.exclude_closed)});
      const data=await api('/job_posts/api/jobs?'+query,{signal:controller.signal});if(run!==sequence)return;
      const last=Math.max(1,Math.ceil(data.total/state.size));if(state.page>last){state.page=last;return loadJobs(scroll);}
      $('results-heading').textContent='검색된 공고 '+data.total.toLocaleString('ko-KR')+'개';list.replaceChildren();
      if(!data.items.length)showState('조건에 맞는 공고가 없어요','검색어를 바꾸거나 조건을 조금 넓혀보세요. 나에게 맞는 기회를 다시 찾아볼까요?');
      else{for(const job of data.items)list.append(card(job));paginate(data.total);}
      if(scroll)$('job-results').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth',block:'start'});
    }catch(error){if(error.name==='AbortError'||run!==sequence)return;$('results-heading').textContent='공고를 불러오지 못했어요';showState('잠시 후 다시 확인해 주세요',error.message,true);}
    finally{if(run===sequence)list.setAttribute('aria-busy','false');}
  }
  function reset(){state={...defaults};fillControls();loadJobs();}
  form.addEventListener('submit',event=>{event.preventDefault();state=readControls();loadJobs();});$('keyword-form').addEventListener('submit',event=>{event.preventDefault();state=readControls();loadJobs();});$('sort-order').addEventListener('change',()=>{state.sort=$('sort-order').value;state.page=1;loadJobs();});$('reset-filters').addEventListener('click',reset);$('clear-search').addEventListener('click',reset);$('retry-search').addEventListener('click',()=>loadJobs());
  async function init(){
    try{
      const options=await api('/job_posts/api/filters');
      for(const [field,values] of [['job',options.jobs],['region',options.regions],['employment',options.employments]])for(const value of values){if(field==='region'&&value==='수도권')continue;const option=element('option',value);option.value=value;selects[field].append(option);}
      for(const key of Object.keys(selects))if(state[key]&&![...selects[key].options].some(option=>option.value===state[key])){const option=element('option',state[key]);option.value=state[key];selects[key].append(option);}
    }catch(error){$('inline-status').textContent=error.message;}
    fillControls();loadJobs();
  }
  init();
})();
