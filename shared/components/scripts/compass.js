(()=> {
  const get=id=>document.getElementById(id),drawer=get('cc-menu'),toggle=get('cc-menu-toggle'),backdrop=get('cc-menu-backdrop'),serviceDialog=get('cc-service-dialog');
  if(!drawer||!toggle||!backdrop||!serviceDialog)return;
  function setMenu(open) {
    drawer.classList.toggle('open',open);
    drawer.inert=!open;
    toggle.setAttribute('aria-expanded',String(open));
    toggle.setAttribute('aria-label',open?'메뉴 닫기':'메뉴 열기');
    backdrop.hidden=!open;
    document.body.classList.toggle('cc-menu-open',open);
    document.querySelector('.cc-header').inert=open;
    document.querySelectorAll('[data-member-content]').forEach(node=>node.inert=open);
    if(open)requestAnimationFrame(()=>get('cc-menu-close').focus());
    else toggle.focus();
  }
  toggle.addEventListener('click',()=>setMenu(!drawer.classList.contains('open')));
  get('cc-menu-close').addEventListener('click',()=>setMenu(false));
  backdrop.addEventListener('click',()=>setMenu(false));
  document.addEventListener('keydown',event=> {
    if(!drawer.classList.contains('open'))return;
    if(event.key==='Escape') {
      event.preventDefault();
      setMenu(false);
    }
    if(event.key==='Tab') {
      const items=[...drawer.querySelectorAll('a[href],button:not([disabled])')],first=items[0],last=items[items.length-1];
      if(event.shiftKey&&document.activeElement===first) {
        event.preventDefault();
        last.focus();
      }
      else if(!event.shiftKey&&document.activeElement===last) {
        event.preventDefault();
        first.focus();
      }
    }
  });
  const pending= {
    training:['나에게 필요한 배움을 준비하고 있어요','교육 추천 기능은 준비 중이에요.\n마이페이지에 자격증과 교육 경험을 정리해 두세요.'],jobs:['더 많은 기회를 모으고 있어요','공고모음은 준비 중이에요.\n지금은 메인 화면의 예시 공고와 관심목록을 확인할 수 있어요.'],courses:['새로운 배움을 모으고 있어요','교육모음은 준비 중이에요.\n나의 교육 경험은 마이페이지에서 등록하고 관리할 수 있어요.']
  };
  document.querySelectorAll('[data-cc-pending]').forEach(button=>button.addEventListener('click',()=> {
    const data=pending[button.dataset.ccPending];
    if(drawer.classList.contains('open'))setMenu(false);
    get('cc-service-title').textContent=data[0];
    get('cc-service-body').textContent=data[1];
    serviceDialog.showModal();
  }));
  get('cc-logout')?.addEventListener('click',async()=> {
    const button=get('cc-logout'),message=get('cc-shell-message');
    button.disabled=true;
    message.hidden=true;
    try {
      const response=await fetch('/api/auth/signout', {
        method:'POST',credentials:'same-origin'
      });
      if(!response.ok) {
        let text='로그아웃하지 못했습니다. 다시 시도해 주세요.';
        try {
          const data=await response.json();
          if(typeof data.detail==='string')text=data.detail;
        }
        catch {
        }
        throw new Error(text);
      }
      location.assign('/signin');
    }
    catch(error) {
      message.textContent=error.message;
      message.hidden=false;
      button.disabled=false;
    }
  });
})();
