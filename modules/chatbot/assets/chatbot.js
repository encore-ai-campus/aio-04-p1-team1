(() => {
  'use strict';
  const dialog = document.getElementById('chatbot-dialog');
  const input = document.getElementById('chatbot-input');
  const log = document.getElementById('chatbot-log');
  const status = document.getElementById('chatbot-status');
  const send = document.getElementById('chatbot-send');
  const shortcuts = [...dialog.querySelectorAll('[data-chatbot-prompt]')];
  const greeting = log.firstElementChild.cloneNode(true);
  let busy = false;
  let history = [];
  let activeRequest = null;
  const paths = new Set(['/job_posts', '/training_posts', '/jd_match', '/training_match']);
  const mascot = document.querySelector('[data-nachimi-sprite]');
  const launcher = document.querySelector('.nachimi-launcher');
  const character = launcher.querySelector('.nachimi-character');
  const notice = document.querySelector('.nachimi-notice');
  const headerButton = document.querySelector('[data-chatbot-open]:not(.nachimi-character):not(.nachimi-invite)');
  let launcherState = {used: false, hidden: false, position: null};
  let noticeTimer;
  let drag = null;
  let suppressClickUntil = 0;
  try {
    const saved = JSON.parse(sessionStorage.getItem('nachimi-launcher') || 'null');
    if (saved) {
      launcherState.used = saved.used === true;
      launcherState.hidden = saved.hidden === true;
      if (Number.isFinite(saved.position?.left) && Number.isFinite(saved.position?.bottom)) {
        launcherState.position = saved.position;
      }
    }
  } catch { /* 저장소 없이도 현재 페이지에서 사용할 수 있습니다. */ }

  function saveLauncher() {
    try { sessionStorage.setItem('nachimi-launcher', JSON.stringify(launcherState)); } catch {}
  }

  function placeLauncher() {
    launcher.hidden = launcherState.hidden;
    launcher.classList.toggle('nachimi-used', launcherState.used);
    if (!launcherState.position || launcher.hidden) return;
    const position = launcherState.position;
    position.left = Math.max(8, Math.min(position.left, window.innerWidth - launcher.offsetWidth - 8));
    // 호버 시 추가되는 안내 문구가 화면 위로 벗어나지 않게 여유를 둡니다.
    position.bottom = Math.max(8, Math.min(position.bottom, window.innerHeight - launcher.offsetHeight - 32));
    launcher.style.left = position.left + 'px';
    launcher.style.bottom = position.bottom + 'px';
    launcher.style.right = 'auto';
  }

  function clearNotice() {
    clearTimeout(noticeTimer);
    notice.hidden = true;
    notice.textContent = '';
  }

  launcher.querySelector('.nachimi-hide').addEventListener('click', () => {
    launcherState.hidden = true;
    placeLauncher();
    saveLauncher();
    clearNotice();
    notice.hidden = false;
    notice.textContent = '챗봇을 숨겼습니다. 다시 사용하려면 상단의 ‘챗봇 사용하기’를 눌러주세요.';
    noticeTimer = setTimeout(clearNotice, 8000);
    headerButton?.focus();
  });

  character.addEventListener('pointerdown', event => {
    if (event.button !== 0 || !event.isPrimary) return;
    const box = launcher.getBoundingClientRect();
    drag = {id: event.pointerId, x: event.clientX, y: event.clientY,
      left: box.left, bottom: window.innerHeight - box.bottom, moved: false};
    character.setPointerCapture(event.pointerId);
  });
  character.addEventListener('pointermove', event => {
    if (!drag || event.pointerId !== drag.id) return;
    const dx = event.clientX - drag.x;
    const dy = event.clientY - drag.y;
    if (Math.hypot(dx, dy) > 5) drag.moved = true;
    if (!drag.moved) return;
    launcher.classList.add('nachimi-dragging');
    launcherState.position = {left: drag.left + dx, bottom: drag.bottom - dy};
    placeLauncher();
  });
  function finishDrag(event) {
    if (!drag || event.pointerId !== drag.id) return;
    if (drag.moved) suppressClickUntil = Date.now() + 500;
    drag = null;
    launcher.classList.remove('nachimi-dragging');
    saveLauncher();
  }
  character.addEventListener('pointerup', finishDrag);
  character.addEventListener('pointercancel', finishDrag);
  character.addEventListener('lostpointercapture', finishDrag);
  character.addEventListener('keydown', event => {
    const step = event.shiftKey ? 40 : 10;
    const delta = {ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, step], ArrowDown: [0, -step]}[event.key];
    if (!delta) return;
    event.preventDefault();
    const box = launcher.getBoundingClientRect();
    launcherState.position = {left: box.left + delta[0], bottom: window.innerHeight - box.bottom + delta[1]};
    placeLauncher();
    saveLauncher();
  });
  window.addEventListener('resize', placeLauncher);
  placeLauncher();
  if (mascot) {
    let pose = Math.floor(Math.random() * 5);
    try {
      const previous = sessionStorage.getItem('nachimi-pose');
      if (previous !== null && /^[0-4]$/.test(previous)) {
        pose = (Number(previous) + 1 + Math.floor(Math.random() * 4)) % 5;
      }
      sessionStorage.setItem('nachimi-pose', String(pose));
    } catch {
      // 저장소를 사용할 수 없는 브라우저에서도 임의의 모습으로 표시합니다.
    }
    mascot.dataset.pose = String(pose);
  }

  function append(speaker, text, actions = [], recommendation = null) {
    const item = document.createElement('div');
    item.className = 'chatbot-message chatbot-' + speaker;
    const label = document.createElement('span');
    label.className = 'chatbot-speaker';
    label.textContent = speaker === 'user' ? '나' : '나침이';
    const message = document.createElement('p');
    message.textContent = text;
    item.append(label, message);
    const links = document.createElement('div');
    links.className = 'chatbot-actions';
    for (const action of actions) {
      const url = new URL(action.url, location.origin);
      if (url.origin !== location.origin || !paths.has(url.pathname)) continue;
      const link = document.createElement('a');
      link.href = url.pathname + url.search;
      link.textContent = action.label + ' →';
      links.append(link);
    }
    if (links.childElementCount) item.append(links);
    if (recommendation) {
      const extra = document.createElement('div');
      extra.className = 'chatbot-recommendation';
      const note = document.createElement('span');
      note.textContent = recommendation.message;
      const link = document.createElement('a');
      link.href = '/training_match';
      link.textContent = 'AI 교육 추천 받기 →';
      extra.append(note, link);
      item.append(extra);
    }
    log.append(item);
    // 대화는 현재 팝업 세션에만 보관하며 DOM 크기를 제한합니다.
    while (log.childElementCount > 60) log.firstElementChild.remove();
    log.scrollTop = log.scrollHeight;
  }

  async function ask(message) {
    message = message.trim();
    if (busy || !message) return;
    busy = true;
    send.disabled = true;
    shortcuts.forEach(button => button.disabled = true);
    append('user', message);
    input.value = '';
    status.textContent = '이야기를 듣고 답변을 준비하고 있어요…';
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 45000);
    const request = {controller, timeout};
    activeRequest = request;
    try {
      const response = await fetch('/api/chatbot/messages', {
        method: 'POST', credentials: 'same-origin', cache: 'no-store',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message, history}), signal: controller.signal,
      });
      if (activeRequest !== request) return;
      if (response.status === 401) {
        location.assign('/signin');
        return;
      }
      const data = await response.json();
      if (activeRequest !== request) return;
      if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : '답변을 불러오지 못했어요. 잠시 후 다시 보내 주세요.');
      append('assistant', data.message, data.actions, data.recommendation);
      const suggestions = data.actions.map(action => action.label).join(', ');
      history.push({role: 'user', content: message}, {
        role: 'assistant', content: data.message + (suggestions ? '\n안내한 기능: ' + suggestions : ''),
      });
      history = history.slice(-12);
      status.textContent = '';
    } catch (error) {
      if (activeRequest !== request) return;
      status.textContent = error.name === 'AbortError' ? '답변이 지연되고 있어요. 잠시 후 다시 보내 주세요.' : error.message || '답변을 불러오지 못했어요. 질문을 다시 보내 주세요.';
      // 실패한 질문을 보존하여 다시 보낼 수 있게 합니다.
      if (!input.value) input.value = message;
    } finally {
      clearTimeout(timeout);
      if (activeRequest === request) {
        activeRequest = null;
        busy = false;
        send.disabled = false;
        shortcuts.forEach(button => button.disabled = false);
        if (dialog.open) input.focus();
      }
    }
  }

  document.querySelectorAll('[data-chatbot-open]').forEach(button => {
    button.addEventListener('click', event => {
      if (button === character && event.detail !== 0 && Date.now() < suppressClickUntil) return;
      clearNotice();
      if (!launcher.contains(button) && launcherState.hidden) {
        launcherState.hidden = false;
        placeLauncher();
        saveLauncher();
        return;
      }
      if (dialog.open) return;
      launcherState.used = true;
      launcherState.hidden = false;
      placeLauncher();
      saveLauncher();
      dialog.showModal();
      document.body.classList.add('chatbot-open');
      input.focus();
    });
  });
  document.getElementById('chatbot-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => {
    document.body.classList.remove('chatbot-open');
    if (activeRequest) {
      clearTimeout(activeRequest.timeout);
      activeRequest.controller.abort();
      activeRequest = null;
    }
    history = [];
    busy = false;
    input.value = '';
    status.textContent = '';
    send.disabled = false;
    shortcuts.forEach(button => button.disabled = false);
    log.replaceChildren(greeting.cloneNode(true));
    log.scrollTop = 0;
  });
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const box = dialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
  });
  document.getElementById('chatbot-form').addEventListener('submit', event => {
    event.preventDefault();
    if (!event.isComposing) ask(input.value);
  });
  shortcuts.forEach(button => button.addEventListener('click', () => ask(button.dataset.chatbotPrompt)));
})();
