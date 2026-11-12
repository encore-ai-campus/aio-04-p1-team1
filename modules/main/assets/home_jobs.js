(()=>{
  'use strict';
  const list=document.getElementById('home-job-list');
  const status=document.getElementById('home-jobs-status');
  const retry=document.getElementById('home-jobs-retry');
  const {api,createRenderer}=window.CompassJobCards;
  const {card}=createRenderer({list,onError:message=>{status.textContent=message;},onNotice:message=>{status.textContent=message;}});
  async function load(){
    list.setAttribute('aria-busy','true');retry.hidden=true;status.textContent='공고를 불러오고 있어요.';
    try{
      const data=await api('/main/api/jobs');
      list.replaceChildren(...data.items.map(card));
      status.textContent=data.items.length?'':'현재 표시할 채용 공고가 없어요.';
    }catch(error){list.replaceChildren();status.textContent=error.message;retry.hidden=false;}
    finally{list.setAttribute('aria-busy','false');}
  }
  retry.addEventListener('click',load);
  window.addEventListener('job-bookmark-changed',async()=>{
    try{
      const data=await api('/api/bookmarks?size=1');
      document.getElementById('saved-total').textContent=data.counts.all;
      document.getElementById('saved-detail').textContent='저장 공고 '+data.counts.job+' · 교육 '+data.counts.course;
    }catch{}
  });
  load();
})();
