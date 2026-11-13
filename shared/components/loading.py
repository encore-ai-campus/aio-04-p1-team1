"""Shared navigation overlay and initial page readiness coordination."""
import base64
from pathlib import Path
import re

_ROOT = Path(__file__).resolve().parent


def apply_loading(html, page="auth"):
    css = (_ROOT / "styles" / "loading.css").read_text(encoding="utf-8")
    script = (_ROOT / "scripts" / "loading.js").read_text(encoding="utf-8")
    image = base64.b64encode((_ROOT / "images" / "nachimi-running.png").read_bytes()).decode("ascii")
    bootstrap = '<script>window.ccLoadingPage="' + page + '";</script><style>' + css + '</style><script>' + script + '</script>'
    overlay = '''<div id="cc-loading" hidden role="status" aria-live="polite" aria-label="화면 준비 중">
      <div class="cc-loading-brand">취준나침반</div>
      <div class="cc-loading-scene" aria-hidden="true"><div class="cc-loading-halo"></div><div class="cc-loading-orbit"></div><div class="cc-loading-shadow"></div><span class="cc-loading-star">✦</span><img src="data:image/png;base64,''' + image + '''" alt="" width="149" height="180"></div>
      <h2 id="cc-loading-title">화면을 준비하고 있습니다</h2><p id="cc-loading-description"></p>
      <div class="cc-loading-dots" aria-hidden="true"><b></b><b></b><b></b></div>
      <p class="cc-loading-footer">YOUR NEXT DIRECTION</p>
      <div id="cc-loading-slow" hidden><p>준비가 평소보다 오래 걸리고 있어요.</p><button type="button" id="cc-loading-reload">다시 불러오기</button></div>
    </div><script>window.CompassLoading.mount();</script>'''
    html = html.replace('</head>', bootstrap + '</head>', 1)
    return re.sub(r'(<body\b[^>]*>)', lambda match: match.group(1) + overlay, html, count=1)
