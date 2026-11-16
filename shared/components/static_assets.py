"""공개 폰트와 로딩 이미지만 버전 URL로 제공한다."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
ASSETS = {
    "A2Z-Regular.woff2": _ROOT / "fonts" / "A2Z-Regular.woff2",
    "A2Z-SemiBold.woff2": _ROOT / "fonts" / "A2Z-SemiBold.woff2",
    "nachimi-running.png": _ROOT / "images" / "nachimi-running.png",
}


@lru_cache(maxsize=3)
def asset_url(name):
    version = sha256(ASSETS[name].read_bytes()).hexdigest()[:16]
    return f"/assets/compass/{version}/{name}"
