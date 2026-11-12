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
  if (mascot) {
    let pose = Math.floor(Math.random() * 4);
    try {
      const previous = sessionStorage.getItem('nachimi-pose');
      if (previous !== null && /^[0-3]$/.test(previous)) {
        pose = (Number(previous) + 1 + Math.floor(Math.random() * 3)) % 4;
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
    button.addEventListener('click', () => {
      if (dialog.open) return;
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
