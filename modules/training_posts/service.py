"""고용24 교육 정규화 및 DB 목록 조회."""
import html
import json
import re
import logging
import os
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from http.client import HTTPException
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
API_URL = "https://www.work24.go.kr/cm/openApi/call/hr/callOpenApiSvcInfo310L01.do"
CATEGORIES = dict(zip(
    [f"{i:02d}" for i in range(1, 25)],
    ["사업관리", "경영·회계·사무", "금융·보험", "교육·자연·사회과학",
     "법률·경찰·소방·교도·국방", "보건·의료", "사회복지·종교",
     "문화·예술·디자인·방송", "운전·운송", "영업판매", "경비·청소",
     "이용·숙박·여행·오락·스포츠", "음식서비스", "건설", "기계", "재료",
     "화학·바이오", "섬유·의복", "전기·전자", "정보통신", "식품가공",
     "인쇄·목재·가구·공예", "환경·에너지·안전", "농림어업"],
))


def escape(value):
    return html.escape(str(value or ""), quote=True)


def safe_link(value):
    try:
        parsed = urlparse(value)
        if parsed.scheme in {"https", "http"} and parsed.hostname in {
            "www.work24.go.kr", "work24.go.kr", "hrd.work24.go.kr", "www.hrd.go.kr"
        }:
            return value
    except ValueError:
        pass
    return ""


def fetch_category(code, start, end):
    """매 호출마다 해당 분류 최신 20개를 API에서 읽습니다. 저장·캐시 없음."""
    name = CATEGORIES[code]
    result = {"code": code, "name": name, "items": [], "available": 0, "error": None}
    key = os.getenv("WORK24_API_KEY", "").strip()
    if not key:
        result["error"] = "같은 폴더의 .env에 WORK24_API_KEY를 설정해 주세요."
        return result
    params = {
        "authKey": key, "returnType": "XML", "outType": "1",
        "pageNum": 1, "pageSize": 20, "srchNcs1": code,
        "srchTraStDt": start.strftime("%Y%m%d"),
        "srchTraEndDt": end.strftime("%Y%m%d"),
        "sort": "DESC", "sortCol": "2",
    }
    request = Request(API_URL + "?" + urlencode(params),
                      headers={"User-Agent": "TrainingList/1.0"})
    try:
        with urlopen(request, timeout=30) as response:
            root = ET.fromstring(response.read())
        total = (root.findtext(".//scn_cnt", "") or "").strip()
        if not total.isdigit():
            result["error"] = "고용24 응답을 확인할 수 없습니다. 인증키의 서비스 신청 상태를 확인해 주세요."
            return result
        result["available"] = int(total)
        seen = set()
        for node in root.findall(".//scn_list"):
            raw = {child.tag: (child.text or "").strip() for child in node}
            identity = tuple(raw.get(field, "") for field in
                             ("trainstCstId", "trprId", "trprDegr"))
            if not all(identity) or not raw.get("title"):
                continue
            if identity in seen:
                continue
            seen.add(identity)
            result["items"].append(raw)
            if len(result["items"]) == 20:
                break
    except (HTTPError, URLError, TimeoutError, OSError, HTTPException):
        # 예외 원문에는 인증키가 포함된 URL이 있을 수 있어 표시하지 않습니다.
        result["error"] = "고용24 연결에 실패했습니다. 잠시 후 새로 조회해 주세요."
    except (ET.ParseError, ValueError):
        result["error"] = "고용24 응답이 올바른 XML 형식이 아닙니다."
    return result


def fetch_all(start, end):
    """분류별 실패를 분리해 한 분야의 오류가 전체 화면을 중단하지 않게 합니다."""
    def fetch_safely(code):
        try:
            return fetch_category(code, start, end)
        except Exception as exc:
            # 인증키가 들어갈 수 있는 예외 메시지·요청 URL은 기록하지 않습니다.
            logging.getLogger("uvicorn.error").warning(
                "Work24 category %s failed (%s)", code, type(exc).__name__
            )
            return {
                "code": code, "name": CATEGORIES[code], "items": [],
                "available": 0,
                "error": "이 분야의 교육 정보를 처리하지 못했습니다. 잠시 후 다시 조회해 주세요.",
            }

    with ThreadPoolExecutor(max_workers=4) as pool:
        return list(pool.map(fetch_safely, CATEGORIES))



def parse_date(value):
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def normalize_course(raw, code):
    title = raw.get("title", "")
    target = raw.get("trainTarget", "")
    evidence = " ".join((target, raw.get("contents", ""), raw.get("titleIcon", "")))
    if raw.get("trainTargetCd") in {"C0031", "C0055", "C0031F"} or "원격" in evidence:
        mode = "online"
    elif "혼합" in evidence:
        mode = "mixed"
    elif "집체" in evidence:
        mode = "offline"
    else:
        mode = "unknown"
    amount = (raw.get("courseMan") or "").replace(",", "").strip()
    cost = int(amount) if re.fullmatch(r"[0-9]+", amount) else None
    start, end = parse_date(raw.get("traStartDate")), parse_date(raw.get("traEndDate"))
    weeks = ((end-start).days + 7) // 7 if start and end and end >= start else None
    tags = []
    for label, pattern in [
        ("SQL", r"sql|데이터베이스"), ("Excel", r"excel|엑셀"),
        ("Python", r"python|파이썬"), ("인사운영", r"인사|인적자원"),
        ("노동관계", r"노무|노동"), ("스프레드시트", r"스프레드시트"),
        ("프로젝트", r"프로젝트"), ("데이터", r"데이터"),
        ("자격증", r"자격|기사|기능사"),
    ]:
        if re.search(pattern, title, re.I):
            tags.append(label)
    if "SQL" in tags or "데이터" in tags:
        badge = "데이터 실무"
    elif "Excel" in tags or re.search(r"사무|행정|보고서", title):
        badge = "사무 실무"
    elif "인사운영" in tags or "노동관계" in tags:
        badge = "인사·노무"
    elif "자격증" in tags:
        badge = "자격증 준비"
    else:
        badge = CATEGORIES[code]
    return {
        "key": "|".join(raw.get(k, "") for k in ("trainstCstId", "trprId", "trprDegr")),
        "title": title, "provider": raw.get("subTitle", ""),
        "category": code, "categoryName": CATEGORIES[code],
        "start": start.isoformat() if start else "",
        "end": end.isoformat() if end else "",
        "weeks": weeks, "mode": mode, "modeEvidence": target,
        "cost": cost, "rawCost": raw.get("courseMan", ""),
        "rawRealCost": raw.get("realMan", ""),
        "address": raw.get("address", ""), "ncsCode": raw.get("ncsCd", ""),
        "round": raw.get("trprDegr", ""), "courseId": raw.get("trprId", ""),
        "url": safe_link(raw.get("titleLink", "")),
        "tags": tags[:3], "badge": badge,
    }



def catalogue_data(start, end):
    """교육 화면은 저장된 Supabase 자료만 읽습니다. API 호출·자동 갱신 없음."""
    from modules.training_posts.repository import read_catalogue
    return read_catalogue(start, end)
