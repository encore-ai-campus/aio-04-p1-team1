"""Shared header, drawer, palette and A2Z fonts. No app routes are registered."""
from pathlib import Path
from html import escape
import base64
import re

_ROOT = Path(__file__).resolve().parent

def apply_member_shell(html, user, current="main"):
    """Fill __CC_CSS__/HEADER/MENU/SCRIPT markers in existing HTML.

    Fonts are embedded so FastAPI string-rendered pages need no static mount.
    Call with the authenticated user, and use body.cc-member-page and
    data-member-content on the page content. Include each marker once.
    """
    css = (_ROOT / "styles" / "compass.css").read_text(encoding="utf-8")
    for name in ("A2Z-Regular.woff2", "A2Z-SemiBold.woff2"):
        encoded = base64.b64encode((_ROOT / "fonts" / name).read_bytes()).decode("ascii")
        css = css.replace('url("' + name + '")', 'url("data:font/woff2;base64,' + encoded + '")')
    header = (_ROOT / "compass-header.html").read_text(encoding="utf-8")
    menu = (_ROOT / "compass-sidebar.html").read_text(encoding="utf-8")
    script = (_ROOT / "scripts" / "compass.js").read_text(encoding="utf-8")
    values = {
        "__CC_CSS__": css,
        "__CC_HEADER__": header,
        "__CC_MENU__": menu,
        "__CC_SCRIPT__": "<script>" + script + "</script>",
        "__CC_MAIN_CURRENT__": ' aria-current="page"' if current == "main" else "",
        "__CC_MYPAGE_CURRENT__": ' aria-current="page"' if current == "mypage" else "",
        "__CC_JD_MATCH_CURRENT__": ' aria-current="page"' if current == "jd_match" else "",
    }
    # User input is escaped and inserted last, never interpreted as a template.
    for marker in ("__CC_CSS__", "__CC_HEADER__", "__CC_MENU__", "__CC_SCRIPT__"):
        html = html.replace(marker, values[marker])
    html = re.sub(r"__CC_(?:MAIN|MYPAGE|JD_MATCH)_CURRENT__", lambda match: values[match.group()], html)
    user_name = user.get("name") if isinstance(user, dict) else user.name
    return html.replace("__CC_USER_NAME__", escape(str(user_name), quote=True))
