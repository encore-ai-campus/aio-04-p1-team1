"""역량 태그 UI. DB 연결 전에는 회원별 브라우저 초안만 저장합니다."""
from html import escape


def apply_skills_ui(html, user, *, editable=False):
    """추후 readDraft/writeDraft만 실제 프로필 API로 교체할 수 있습니다."""
    block = EDITOR if editable else SUMMARY
    block = block.replace('__SKILLS_USER_ID__', escape(str(user['id']), quote=True))
    html = html.replace('__SKILLS_CONTENT__', block)
    html = html.replace('__SKILLS_CSS__', CSS)
    return html.replace('__SKILLS_SCRIPT__', '<script>' + SCRIPT + '</script>')


SUMMARY = '''
<div class="skills-section" data-skills-root data-user-id="__SKILLS_USER_ID__">
  <div class="skills-heading"><h3>나의 역량</h3><span class="skills-storage-badge">브라우저 임시 저장</span></div>
  <div class="skills-tags" data-skills-list aria-label="등록한 역량"></div>
  <p class="skills-help" data-skills-empty>아직 등록한 역량이 없어요. 정보 수정에서 추가해 주세요.</p>
  <p class="skills-help">현재 브라우저에만 보관됩니다. DB 저장과 공고 적합도 분석 연결은 추후 적용됩니다.</p>
  <p class="skills-message" data-skills-message role="status" aria-live="polite"></p>
</div>'''

EDITOR = '''
<section class="skills-section skills-editor" data-skills-root data-skills-editable data-user-id="__SKILLS_USER_ID__" aria-labelledby="skills-title">
  <div class="skills-heading"><h3 id="skills-title">나의 역량</h3><span class="skills-storage-badge">브라우저 임시 저장</span></div>
  <p class="skills-help" id="skills-help">Python, SQL, 문제 해결 등 나의 역량을 입력해 주세요. Enter 또는 쉼표로 추가할 수 있어요. 최대 20개, 각 30자까지 등록할 수 있습니다.</p>
  <label for="skills-input">역량 추가</label>
  <div class="skills-input-row"><input id="skills-input" type="text" autocomplete="off" placeholder="예: Python, SQL" aria-describedby="skills-help skills-message"><button class="button" type="button" id="skills-add">추가</button></div>
  <div class="skills-tags" data-skills-list aria-label="등록할 역량"></div>
  <p class="skills-help" data-skills-empty>등록한 역량이 없어요. 역량을 추가해 보세요.</p>
  <p class="skills-message" id="skills-message" data-skills-message role="status" aria-live="polite"></p>
  <p class="skills-help">변경 내용 저장을 누르면 역량은 현재 브라우저에만 임시 보관됩니다. 다른 기기에는 공유되지 않으며, 아직 DB나 적합도 분석에 전달되지 않습니다.</p>
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
  const storageKey = 'career-compass:skills-draft:v1:' + root.dataset.userId;
  const maxItems = 20, maxLength = 30;
  let skills = [], readFailed = false, composing = false;

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
  // DB 연결 시 이 두 함수의 구현을 서버 프로필 API 호출로 교체합니다.
  function readDraft() {
    const raw = localStorage.getItem(storageKey);
    if (!raw) return [];
    const data = JSON.parse(raw);
    if (data.version !== 1) throw new Error('지원하지 않는 임시 저장 형식입니다.');
    return check(data.skills);
  }
  function writeDraft(values) {
    localStorage.setItem(storageKey, JSON.stringify({version: 1, skills: check(values)}));
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
          skills.splice(index, 1); render();
          message.textContent = '변경 내용 저장을 눌러 임시 보관해 주세요.'; input.focus();
        });
        tag.append(remove);
      }
      list.append(tag);
    });
    empty.hidden = skills.length > 0;
  }
  function addInput() {
    const raw = input.value.trim();
    if (!raw) { showError('추가할 역량을 입력해 주세요.'); return false; }
    const incoming = raw.split(/[,，]/).map(normalize).filter(Boolean);
    if (!incoming.length) { showError('추가할 역량을 입력해 주세요.'); return false; }
    try {
      const next = check([...skills, ...incoming]);
      skills = next; input.value = ''; input.removeAttribute('aria-invalid'); render();
      message.textContent = '변경 내용 저장을 눌러 임시 보관해 주세요.';
      return true;
    } catch (error) {
      showError(error.message); input.setAttribute('aria-invalid', 'true'); return false;
    }
  }
  try { skills = readDraft(); }
  catch (error) {
    readFailed = true;
    showError('이 브라우저의 역량 임시 데이터를 불러오지 못했습니다. 기존 임시 데이터는 덮어쓰지 않습니다.');
  }
  render();
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
      if (readFailed) { showError('역량 임시 데이터는 덮어쓰지 않습니다. 이름 변경은 계속할 수 있어요.'); return true; }
      if (input.value.trim() && !addInput()) { input.focus(); return false; }
      return true;
    },
    commit() {
      if (readFailed) throw new Error('기존 역량 임시 데이터를 덮어쓰지 않았습니다.');
      try { writeDraft(skills); }
      catch (error) { throw new Error('역량을 임시 저장하지 못했습니다. 브라우저 저장 공간과 설정을 확인해 주세요.'); }
      message.textContent = '역량을 이 브라우저에 임시 보관했습니다. 아직 DB에는 저장되지 않았습니다.';
    }
  };
})();
'''
