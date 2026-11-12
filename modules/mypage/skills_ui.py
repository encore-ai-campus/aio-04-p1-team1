"""역량 태그 UI. 공통 인증 API를 통해 profiles.skills를 저장·조회합니다."""
from html import escape


def apply_skills_ui(html, user, *, editable=False):
    """기존 카드와 편집 UI를 유지하면서 DB 저장 API를 연결합니다."""
    block = EDITOR if editable else SUMMARY
    block = block.replace('__SKILLS_USER_ID__', escape(str(user['id']), quote=True))
    html = html.replace('__SKILLS_CONTENT__', block)
    html = html.replace('__SKILLS_CSS__', CSS)
    return html.replace('__SKILLS_SCRIPT__', '<script>' + SCRIPT + '</script>')


SUMMARY = '''
<div class="skills-section" data-skills-root data-user-id="__SKILLS_USER_ID__">
  <div class="skills-tags" data-skills-list aria-label="등록한 역량"></div>
  <p class="skills-help" data-skills-empty>아직 등록한 역량이 없어요. 역량 수정에서 추가해 주세요.</p>
  <p class="skills-help">적합도 분석에 활용합니다.</p>
  <p class="skills-message" data-skills-message role="status" aria-live="polite"></p>
</div>'''

EDITOR = '''
<section class="skills-section skills-editor" data-skills-root data-skills-editable data-user-id="__SKILLS_USER_ID__" aria-labelledby="skills-title">
  <div class="skills-heading"><h3 id="skills-title">나의 역량</h3></div>
  <p class="skills-help" id="skills-help">Python, SQL, 문제 해결 등 나의 역량을 입력해 주세요. Enter 또는 쉼표로 추가할 수 있어요. 최대 20개, 각 30자까지 등록할 수 있습니다.</p>
  <label for="skills-input">역량 추가</label>
  <div class="skills-input-row"><input id="skills-input" type="text" autocomplete="off" placeholder="예: Python, SQL" aria-describedby="skills-help skills-message"><button class="button" type="button" id="skills-add">추가</button></div>
  <div class="skills-tags" data-skills-list aria-label="등록할 역량"></div>
  <p class="skills-help" data-skills-empty>등록한 역량이 없어요. 역량을 추가해 보세요.</p>
  <p class="skills-message" id="skills-message" data-skills-message role="status" aria-live="polite"></p>
  <p class="skills-help">적합도 분석에 활용합니다.</p>
</section>'''

CSS = r'''
.skills-section{margin-top:24px;padding-top:22px;border-top:1px solid var(--cc-border);min-width:0}
.skills-heading{display:flex;align-items:center;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-bottom:12px}
.skills-heading h3{font-size:15px;line-height:1.6;margin:0;color:var(--cc-text)}
.skills-storage-badge{font-size:10px;color:#73704e;background:#fff7dc;border:1px solid #f0e5bd;padding:3px 8px;border-radius:6px}
.skills-tags{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 10px;min-width:0}
.skills-tag{display:inline-flex;align-items:center;gap:7px;max-width:100%;padding:6px 10px;border:1px solid #e1e4dd;border-radius:8px;background:white;color:var(--cc-text);font-size:13px;line-height:1.5}
.skills-tag-text{overflow-wrap:anywhere;min-width:0}
.skills-tag-hash{color:#8b917f;margin-right:2px}
.skills-tag-remove{display:grid;place-items:center;flex-shrink:0;border:0;background:transparent;color:#697161;min-width:28px;min-height:28px;padding:0;cursor:pointer;border-radius:5px}
.skills-tag-remove:hover{background:var(--cc-background)}
.skills-help{font-size:11px;line-height:1.8;color:var(--cc-muted);margin:8px 0}
.skills-message{font-size:12px;line-height:1.7;color:#a73c28;margin:8px 0;min-height:0}
.skills-message:empty{display:none}
.skills-input-row{display:flex;align-items:center;gap:8px}
.skills-input-row input{flex:1;min-width:0;width:auto}
.profile .skills-input-row .button{margin:0;min-height:45px;flex-shrink:0}
.profile .skills-editor label{margin-top:14px}
.skills-tag-remove:focus-visible{outline:3px solid #93823c;outline-offset:3px}
'''

SCRIPT = r'''
(() => {
  const root = document.querySelector('[data-skills-root]');
  if (!root) return;
  const editable = root.hasAttribute('data-skills-editable');
  const list = root.querySelector('[data-skills-list]');
  const empty = root.querySelector('[data-skills-empty]');
  const message = root.querySelector('[data-skills-message]');
  const input = editable ? document.getElementById('skills-input') : null;
  const maxItems = 20, maxLength = 30;
  let skills = [], loaded = false, saving = false, composing = false;

  function normalize(value) {
    return value.trim().replace(/^#+/, '').trim().replace(/\s+/g, ' ');
  }
  function check(values) {
    if (!Array.isArray(values) || values.length > maxItems) throw new Error('역량은 최대 20개까지 등록할 수 있어요.');
    const result = [], seen = new Set();
    for (const value of values) {
      if (typeof value !== 'string') throw new Error('저장된 역량 형식을 확인할 수 없어요.');
      const tag = normalize(value);
      if (!tag || [...tag].length > maxLength || /[\u0000-\u001f\u007f]/.test(tag)) throw new Error('역량은 공백을 제외한 1~30자로 입력해 주세요.');
      const key = tag.toLowerCase();
      if (seen.has(key)) throw new Error('이미 추가한 역량입니다.');
      seen.add(key); result.push(tag);
    }
    return result;
  }
  async function skillsRequest(method, values) {
    const options = {method, credentials: 'same-origin', cache: 'no-store'};
    if (method === 'PUT') {
      options.headers = {'Content-Type': 'application/json'};
      options.body = JSON.stringify({skills: check(values)});
    }
    const response = await fetch('/api/mypage/skills', options);
    if (response.status === 401) { location.assign('/signin'); throw new Error('다시 로그인해 주세요.'); }
    const data = await response.json();
    if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : '역량을 처리하지 못했습니다.');
    return check(data.skills);
  }
  function setEditingDisabled(disabled) {
    if (!editable) return;
    input.disabled = disabled;
    document.getElementById('skills-add').disabled = disabled;
    list.querySelectorAll('button').forEach(button => button.disabled = disabled);
  }
  function showError(text) { message.textContent = text; }
  function render() {
    list.replaceChildren();
    skills.forEach((skill, index) => {
      const tag = document.createElement('span'); tag.className = 'skills-tag';
      const text = document.createElement('span'); text.className = 'skills-tag-text';
      const hash = document.createElement('span'); hash.className = 'skills-tag-hash'; hash.textContent = '#';
      text.append(hash, document.createTextNode(skill)); tag.append(text);
      if (editable) {
        const remove = document.createElement('button');
        remove.type = 'button'; remove.className = 'skills-tag-remove'; remove.textContent = '×';
        remove.setAttribute('aria-label', skill + ' 역량 삭제');
        remove.addEventListener('click', () => {
          if (saving || !loaded) return;
          skills.splice(index, 1); render();
          message.textContent = '변경 내용 저장을 눌러 주세요.'; input.focus();
        });
        tag.append(remove);
      }
      list.append(tag);
    });
    empty.hidden = skills.length > 0;
  }
  function addInput() {
    if (!loaded || saving) return false;
    const raw = input.value.trim();
    if (!raw) { showError('추가할 역량을 입력해 주세요.'); return false; }
    const incoming = raw.split(/[,，]/).map(normalize).filter(Boolean);
    if (!incoming.length) { showError('추가할 역량을 입력해 주세요.'); return false; }
    try {
      const next = check([...skills, ...incoming]);
      skills = next; input.value = ''; input.removeAttribute('aria-invalid'); render();
      message.textContent = '변경 내용 저장을 눌러 주세요.';
      return true;
    } catch (error) {
      showError(error.message); input.setAttribute('aria-invalid', 'true'); return false;
    }
  }
  async function loadSkills() {
    setEditingDisabled(true);
    message.textContent = '역량을 불러오는 중이에요.';
    try {
      skills = await skillsRequest('GET'); loaded = true; render(); message.textContent = '';
      window.dispatchEvent(new CustomEvent('profile-skills-loaded', {detail: skills}));
    } catch (error) {
      loaded = false; showError(error.message + ' 새로고침 후 다시 시도해 주세요.');
    } finally { setEditingDisabled(!loaded); }
  }
  window.addEventListener('profile-skills-saved', event => {
    skills = check(event.detail); loaded = true; render(); message.textContent = '';
  });
  loadSkills();
  if (!editable) return;
  document.getElementById('skills-add').addEventListener('click', () => { addInput(); input.focus(); });
  input.addEventListener('compositionstart', () => { composing = true; });
  input.addEventListener('compositionend', () => { composing = false; });
  input.addEventListener('keydown', event => {
    if (composing || event.isComposing || event.keyCode === 229) return;
    if (event.key === 'Enter' || event.key === ',' || event.key === '，') {
      event.preventDefault(); addInput();
    }
  });
  input.addEventListener('input', () => input.removeAttribute('aria-invalid'));
  window.CompassSkillsDraft = {
    prepare() {
      if (!loaded) return true; // 이름 저장은 유지하고 역량 덮어쓰기는 commit에서 막습니다.
      if (input.value.trim() && !addInput()) { input.focus(); return false; }
      return true;
    },
    async commit() {
      if (!loaded) throw new Error('역량을 불러오지 못해 저장하지 않았습니다. 새로고침 후 다시 시도해 주세요.');
      saving = true; setEditingDisabled(true);
      try {
        const next = await skillsRequest('PUT', skills);
        skills = next; render(); message.textContent = '역량을 저장했습니다.';
      } catch (error) {
        showError(error.message); throw error;
      } finally { saving = false; setEditingDisabled(false); }
    }
  };
})();
'''
