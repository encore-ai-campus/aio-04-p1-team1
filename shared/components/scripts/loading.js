(() => {
  'use strict';
  const root = document.documentElement, tasks = [];
  const page = window.ccLoadingPage;
  let active = false, leaving = false, timer, previousFocus;
  let kind = page === 'mypage' ? 'mypage' : 'main';
  try {
    const pending = JSON.parse(sessionStorage.getItem('cc-loading-navigation'));
    sessionStorage.removeItem('cc-loading-navigation');
    if (pending && pending.path === location.pathname && Date.now() - pending.at < 120000) kind = pending.kind;
  } catch {}
  const copy = {
    login: ['로그인 중입니다', '나침이가 당신의 취업 여정을 준비하고 있어요.'],
    main: ['메인으로 이동 중입니다', '나침이가 당신의 취업 여정을 준비하고 있어요.'],
    mypage: ['마이페이지로 이동 중입니다', '나침이가 나의 활동과 프로필을 모으고 있어요.'],
    jd_match: ['적합도를 분석하고 있습니다', '나침이가 공고와 내 역량을 꼼꼼히 비교하고 있어요.'],
    jd_match_navigation: ['적합도 분석 화면으로 이동하고 있습니다', '나침이가 적합도 분석 화면을 준비하고 있어요.']
  };
  function mount() {
    const overlay = document.getElementById('cc-loading');
    if (!overlay) return;
    overlay.hidden = !active;
    if (active) document.body.setAttribute('aria-busy', 'true');
    const text = copy[kind] || copy.main;
    document.getElementById('cc-loading-title').textContent = text[0];
    const description = document.getElementById('cc-loading-description');
    description.replaceChildren(document.createTextNode(text[1]), document.createElement('br'), document.createTextNode('잠시만 기다려 주세요.'));
    document.getElementById('cc-loading-reload').onclick = () => location.reload();
  }
  function show(nextKind) {
    kind = nextKind; active = true;
    previousFocus = document.activeElement;
    root.classList.add('cc-loading-active');
    if (document.body) document.body.setAttribute('aria-busy', 'true');
    mount(); clearTimeout(timer);
    const slow = document.getElementById('cc-loading-slow');
    if (slow) slow.hidden = true;
    timer = setTimeout(() => {
      const hint = document.getElementById('cc-loading-slow');
      if (active && hint) hint.hidden = false;
    }, 20000);
  }
  function hide() {
    active = false; clearTimeout(timer);
    root.classList.remove('cc-loading-active');
    document.body?.removeAttribute('aria-busy');
    const overlay = document.getElementById('cc-loading');
    if (overlay) overlay.hidden = true;
    if (previousFocus?.isConnected) previousFocus.focus({preventScroll: true});
  }
  function navigate(path, nextKind) {
    leaving = true; show(nextKind);
    try { sessionStorage.setItem('cc-loading-navigation', JSON.stringify({path: new URL(path, location.href).pathname, kind: nextKind, at: Date.now()})); } catch {}
    // Paint the outgoing overlay before waiting for the next document's server response.
    requestAnimationFrame(() => requestAnimationFrame(() => location.assign(path)));
  }
  window.CompassLoading = {mount, show, hide, navigate, track(promise) {
    tasks.push(Promise.resolve(promise).catch(() => {}));
    return promise;
  }};
  if (page === 'main' || page === 'mypage') show(kind);
  document.addEventListener('click', event => {
    if (event.defaultPrevented || event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    const link = event.target.closest('a[href]');
    if (!link || link.download || (link.target && link.target !== '_self')) return;
    const url = new URL(link.href, location.href);
    if (url.origin !== location.origin || !/^\/(main|mypage|jd_match)(\/|$)/.test(url.pathname)) return;
    if (url.pathname === location.pathname && url.search === location.search) return;
    event.preventDefault();
    const nextKind = url.pathname.startsWith('/mypage') ? 'mypage'
      : url.pathname.startsWith('/jd_match') ? 'jd_match_navigation' : 'main';
    navigate(url.href, nextKind);
  });
  window.addEventListener('load', async () => {
    if (page === 'auth') return;
    await Promise.allSettled([document.fonts.ready, ...tasks]);
    if (leaving) return;
    await Promise.allSettled([...document.images].map(img => img.decode ? img.decode() : Promise.resolve()));
    requestAnimationFrame(() => requestAnimationFrame(() => { if (!leaving) hide(); }));
  }, {once: true});
  window.addEventListener('pageshow', event => { if (event.persisted) { leaving = false; hide(); } });
})();
