AUTH_HEADER = '<header><a class="brand" href="/signin"><span class="brand-icon" aria-hidden="true"><svg viewBox="0 0 32 32"><path d="M23 8 18 19 8 24 13 13Z" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="m23 8-7 8-3-3Z" fill="currentColor"/></svg></span>취준나침반</a><span class="header-note">한 번에 찾고, 한 걸음씩 준비해요.</span></header>'
MEMBER_HEADER = '''<header><div class="header-inner"><a class="brand" href="/main"><span class="brand-icon" aria-hidden="true">⤢</span>취준나침반</a><nav class="nav" aria-label="상단 메뉴"><span class="username">__NAME__님</span><a href="/main">메인</a><a href="/mypage">마이페이지</a><button class="logout" id="logout" type="button">로그아웃</button></nav></div></header>
<script>
document.getElementById('logout').addEventListener('click', async (event) => {
  const button = event.currentTarget;
  button.disabled = true;
  try {
    const response = await fetch('/api/auth/signout', { method: 'POST' });
    if (!response.ok) throw new Error('로그아웃에 실패했습니다. 다시 시도해 주세요.');
    location.assign('/signin');
  } catch (error) {
    alert(error.message || '로그아웃에 실패했습니다. 다시 시도해 주세요.');
    button.disabled = false;
  }
});
</script>'''


def render_header(member=False):
    return MEMBER_HEADER if member else AUTH_HEADER
