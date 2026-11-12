(()=>{
  'use strict';
  const $=id=>document.getElementById(id);
  const form=$('filter-form'), keyword=$('keyword'), list=$('job-list'), pages=$('pagination');
  const defaults={q:'',job:'',region:'',career:'',employment:'',exclude_closed:true,sort:'default',page:1,size:8};
  const selects={job:$('job-filter'),region:$('region-filter'),career:$('career-filter'),employment:$('employment-filter')};
  let state={...defaults}, controller=null, sequence=0, toastTimer=null;
  const {element,api}=window.CompassJobCards;
  const {card}=window.CompassJobCards.createRenderer({list,onError:message=>{$('inline-status').textContent=message;},onNotice:toast});
  const urlParams=new URLSearchParams(location.search);
  for(const key of ['q','job','region','career','employment'])state[key]=urlParams.get(key)||'';
  state.sort=['default','deadline','company'].includes(urlParams.get('sort'))?urlParams.get('sort'):'default';
  state.exclude_closed=urlParams.get('exclude_closed')!=='false';
  state.page=Math.max(1,Math.min(10000,Number.parseInt(urlParams.get('page'),10)||1));
  function params(){const query=new URLSearchParams();for(const [key,value] of Object.entries(state)){if(value!==''&&value!==defaults[key])query.set(key,String(value));}return query;}
  function syncUrl(){const query=params().toString();history.replaceState(null,'',location.pathname+(query?'?'+query:''));}
  function fillControls(){keyword.value=state.q;for(const [key,select] of Object.entries(selects))select.value=state[key];$('exclude-closed').checked=state.exclude_closed;$('sort-order').value=state.sort;}
  function readControls(){const next={...state,q:keyword.value.trim(),sort:$('sort-order').value,exclude_closed:$('exclude-closed').checked,page:1};for(const [key,select] of Object.entries(selects))next[key]=select.value;return next;}
  function toast(message){$('bookmark-toast').textContent=message;$('bookmark-toast').hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('bookmark-toast').hidden=true,3000);}
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
