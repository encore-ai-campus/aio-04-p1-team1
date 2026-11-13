"""공통 챗봇 팝업과 고정 나침이 펫. 공통 UI의 폰트·색상을 사용합니다."""

from pathlib import Path


def asset_url(name):
    asset = Path(__file__).with_name("assets") / name
    return f"/api/chatbot/assets/{name}?v={asset.stat().st_mtime_ns}"


def render_launcher():
    root = Path(__file__).with_name("assets")
    return (root / "launcher.html").read_text(encoding="utf-8").replace(
        "__NACHIMI_POSES__", asset_url("nachimi-poses.png")
    ).replace(
        "__NACHIMI_QUESTION__", asset_url("nachimi-question.png")
    )


def render_widget():
    root = Path(__file__).with_name("assets")
    avatar = asset_url("nachimi-question.png")
    return (
        '<style>#chatbot-dialog{--chatbot-avatar:url("' + avatar + '")}'
        + (root / "chatbot.css").read_text(encoding="utf-8") + "</style>"
        + (root / "chatbot.html").read_text(encoding="utf-8")
        + render_launcher()
        + "<script>" + (root / "chatbot.js").read_text(encoding="utf-8") + "</script>"
    )
