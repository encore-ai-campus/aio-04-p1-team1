"""고용24 목록 API를 검색해 원본 XML과 항목별 JSON을 저장합니다.

python -m modules.training_posts.service --keyword 파이썬 --start 20261109 --end 20261231
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET
from zoneinfo import ZoneInfo

from modules.training_posts.model import FIELD_DESCRIPTIONS, TrainingSearchResult


API_URL = "https://www.work24.go.kr/cm/openApi/call/hr/callOpenApiSvcInfo310L01.do"
MODULE_DIR = Path(__file__).resolve().parent


class Work24APIError(RuntimeError):
    def __init__(self, message, response_xml=None):
        super().__init__(message)
        self.response_xml = response_xml


def _tag(element):
    return element.tag.rsplit("}", 1)[-1]


def parse_training_xml(xml: str) -> TrainingSearchResult:
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as exc:
        raise Work24APIError("고용24 응답이 올바른 XML이 아닙니다.", xml) from exc
    errors = ["".join(node.itertext()).strip() for node in root.iter() if _tag(node) == "error"]
    if errors:
        raise Work24APIError("고용24 API 오류: " + " / ".join(errors), xml)
    if _tag(root) != "HRDNet":
        raise Work24APIError("예상한 HRDNet 목록 응답이 아닙니다.", xml)
    metadata = {_tag(node): (node.text or "").strip() for node in root}
    try:
        total, page, size = (int(metadata[name]) for name in ("scn_cnt", "pageNum", "pageSize"))
        if total < 0 or page < 1 or size < 1:
            raise ValueError("invalid pagination")
    except (KeyError, ValueError) as exc:
        raise Work24APIError("검색 건수 또는 페이지 정보가 없습니다.", xml) from exc
    courses = [{_tag(child): "".join(child.itertext()).strip() for child in node}
               for node in root.iter() if _tag(node) == "scn_list"]
    if (total == 0 and courses) or (total > 0 and not courses and page == 1):
        raise Work24APIError("검색 건수와 과정 목록이 일치하지 않습니다.", xml)
    return TrainingSearchResult(total, page, size, courses)


def build_search_params(*, keyword: str, start: str, end: str, institution="", region="", ncs="", page=1, page_size=1):
    for value in (start, end):
        if len(value) != 8 or not value.isdecimal():
            raise ValueError("검색 날짜는 YYYYMMDD 형식이어야 합니다.")
        datetime.strptime(value, "%Y%m%d")
    if start > end:
        raise ValueError("검색 시작일이 종료일보다 늦습니다.")
    if not 1 <= page <= 1000 or not 1 <= page_size <= 100:
        raise ValueError("페이지는 1~1000, 페이지당 건수는 1~100이어야 합니다.")
    if ncs and ncs not in {f"{code:02d}" for code in range(1, 25)}:
        raise ValueError("NCS 대분류는 01~24 중 하나여야 합니다.")
    params = {"returnType": "XML", "outType": "1", "pageNum": str(page), "pageSize": str(page_size),
              "srchTraStDt": start, "srchTraEndDt": end, "sort": "ASC", "sortCol": "2"}
    for name, value in [("srchTraProcessNm", keyword), ("srchTraOrganNm", institution), ("srchTraArea1", region), ("srchNcs1", ncs)]:
        if value.strip():
            params[name] = value.strip()
    return params


def search_training_courses(api_key: str, **conditions):
    """리턴: 파싱 결과, 원본 XML, 인증키를 제외한 검색 조건."""
    if not api_key or "&" in api_key or api_key.startswith("authKey="):
        raise ValueError("API 키에는 인증키 값만 넣으세요. URL이나 &returnType= 등의 파라미터는 제외합니다.")
    params = build_search_params(**conditions)
    request = Request(API_URL + "?" + urlencode({**params, "authKey": api_key}),
                      headers={"Accept": "application/xml", "User-Agent": "CareerCompass/1.0"})
    try:
        with urlopen(request, timeout=30) as response:
            raw = response.read().decode(response.headers.get_content_charset() or "utf-8-sig")
    except HTTPError as exc:
        raise Work24APIError(f"고용24 HTTP 오류: {exc.code}") from None
    except (URLError, TimeoutError):
        raise Work24APIError("고용24에 연결하지 못했습니다. 네트워크와 인증키 사용 환경을 확인하세요.") from None
    raw = raw.replace(api_key, "<redacted>")
    return parse_training_xml(raw), raw, params


def load_api_key():
    from dotenv import load_dotenv
    load_dotenv(MODULE_DIR.parents[1] / ".env", override=False)
    key = next((os.environ[name].strip() for name in (
        "WORK24_API_KEY", "TRAININING_API_KEY", "TRAINING_API_KEY"
    ) if os.environ.get(name, "").strip()), "")
    if not key:
        raise ValueError(".env에 WORK24_API_KEY를 설정하세요. 기존 TRAININING_API_KEY도 지원합니다.")
    return key


def main():
    today = datetime.now(ZoneInfo("Asia/Seoul")).date()
    parser = argparse.ArgumentParser(description="고용24 훈련과정 목록 API 항목 확인")
    parser.add_argument("--keyword", default="파이썬", help="훈련과정명 검색어")
    parser.add_argument("--start", default=today.strftime("%Y%m%d"), help="훈련 시작일 범위: YYYYMMDD")
    parser.add_argument("--end", default=(today + timedelta(days=90)).strftime("%Y%m%d"))
    parser.add_argument("--institution", default="", help="훈련기관명")
    parser.add_argument("--region", default="", help="지역 대분류 코드, 예: 서울 11")
    parser.add_argument("--ncs", default="", help="NCS 대분류 01~24")
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--page-size", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=MODULE_DIR / "results")
    parser.add_argument("--list-fields", action="store_true", help="공식 응답 항목만 출력 (API 요청 없음)")
    parser.add_argument("--xml", type=Path, help="저장된 XML로 항목 확인 (API 요청 없음)")
    args = parser.parse_args()
    if args.list_fields:
        print(json.dumps(FIELD_DESCRIPTIONS, ensure_ascii=False, indent=2))
        return
    try:
        if args.xml:
            raw = args.xml.read_text(encoding="utf-8-sig")
            result, params = parse_training_xml(raw), {"input_file": str(args.xml)}
        else:
            key = load_api_key()
            result, raw, params = search_training_courses(key, keyword=args.keyword, start=args.start, end=args.end,
                institution=args.institution, region=args.region, ncs=args.ncs, page=args.page, page_size=args.page_size)
        report = {"endpoint": API_URL, "request": params, "total_count": result.total_count,
                  "page_num": result.page_num, "page_size": result.page_size,
                  "returned_count": len(result.courses), "inspection": result.inspect()}
        args.output_dir.mkdir(parents=True, exist_ok=True)
        (args.output_dir / "training_response.xml").write_text(raw, encoding="utf-8")
        (args.output_dir / "training_inspection.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if not result.courses:
            print("검색 결과가 없습니다. 과정명이나 훈련 시작일 범위를 변경하세요.")
    except Work24APIError as exc:
        if exc.response_xml:
            args.output_dir.mkdir(parents=True, exist_ok=True)
            (args.output_dir / "training_error.xml").write_text(exc.response_xml, encoding="utf-8")
        parser.exit(1, f"조회 실패: {exc}\n")
    except ImportError:
        parser.exit(1, "python -m pip install -r requirements.txt 를 실행하세요.\n")
    except (ValueError, OSError) as exc:
        parser.exit(1, f"조회 실패: {exc}\n")


if __name__ == "__main__":
    main()
