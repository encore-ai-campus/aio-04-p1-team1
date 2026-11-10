"""원티드 상세 HTML의 __NEXT_DATA__에서 공고를 추출합니다.

실행: python3 -m modules.job_posts.service https://www.wanted.co.kr/wd/391602
저장된 HTML 사용: python3 -m modules.job_posts.service --html /tmp/wanted.html
"""

import argparse
import json
import re
from collections import Counter
from dataclasses import asdict
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from uuid import NAMESPACE_URL, UUID, uuid5

from modules.job_posts.model import WantedJobPost


DEFAULT_URL = "https://www.wanted.co.kr/wd/391602"


class WantedCrawlError(RuntimeError):
    """네트워크 오류 또는 원티드 HTML 구조 변경."""


class _NextDataParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.collecting = False
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("id") == "__NEXT_DATA__":
            self.collecting = True

    def handle_data(self, data):
        if self.collecting:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == "script":
            self.collecting = False


def _canonical_url(url: str) -> str:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.netloc not in {"www.wanted.co.kr", "wanted.co.kr"}
        or not re.fullmatch(r"/wd/\d+/?", parsed.path)
    ):
        raise ValueError("https://www.wanted.co.kr/wd/공고번호 형식의 URL을 입력하세요.")
    return f"https://www.wanted.co.kr/wd/{int(parsed.path.strip('/').split('/')[-1])}"


def _text(value):
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("원문 텍스트의 타입이 올바르지 않습니다.")
    return value.strip() or None


def _career_fields(career: dict):
    if not career:
        return "미확인", None, None
    start, end = career.get("annual_from"), career.get("annual_to")
    for value in (start, end):
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError("경력 연수가 올바르지 않습니다.")
    if start is not None and end is not None and start > end:
        raise ValueError("최소 경력이 최대 경력보다 큽니다.")
    newbie, expert = career.get("is_newbie"), career.get("is_expert")
    if newbie is True and expert is True:
        # 0~1년은 원티드 헤더에서 '신입'으로 표시됩니다.
        career_type = "신입" if start == 0 and end == 1 else "신입·경력"
    elif newbie is True:
        career_type = "신입"
    elif expert is True:
        career_type = "경력"
    elif newbie is False and expert is False:
        career_type = "무관"
    else:
        career_type = "미확인"
    return career_type, start * 12 if start is not None else None, (
        end * 12 if end is not None and end != 100 else None
    )


def _deadline_fields(job: dict, html: str):
    # 본문의 '채용 시' 표현이 아니라 마감일 영역만 사용합니다.
    match = re.search(r'<article\b[^>]*class="[^"]*JobDueTime[^\"]*"[^>]*>(.*?)</article>', html, re.S)
    label = re.sub(r"<[^>]+>", "", match.group(1)) if match else ""
    due = job.get("due_time")
    if due:
        parsed = datetime.fromisoformat(due.replace("Z", "+00:00"))
        # 원본에 표시된 달력 날짜를 유지합니다. 시간대 변환으로 날짜를 바꾸지 않습니다.
        return "날짜 지정", parsed.date().isoformat()
    if "상시" in label:
        return "상시", None
    if re.search(r"채용\s*시", label):
        return "채용 시", None
    return "미확인", None


def parse_wanted_html(html: str, url: str = DEFAULT_URL, *, region_ids=None) -> WantedJobPost:
    """접힌 우대사항도 포함된 HTML 내 JSON을 파싱합니다. 외부 API는 호출하지 않습니다."""
    url = _canonical_url(url)
    parser = _NextDataParser()
    parser.feed(html)
    if not parser.parts:
        raise WantedCrawlError("__NEXT_DATA__가 없습니다. 차단 응답 또는 HTML 구조를 확인하세요.")
    try:
        payload = json.loads("".join(parser.parts))
        job = payload["props"]["pageProps"]["initialData"]
        if not isinstance(job, dict) or not isinstance(job.get("company"), dict):
            raise ValueError("공고 데이터가 없습니다.")
        company = job["company"]["company_name"]
        position = job["position"]
        if not company or not position:
            raise ValueError("회사명 또는 직무명이 없습니다.")
        if str(job.get("id")) != url.rsplit("/", 1)[-1]:
            raise ValueError("요청 URL과 HTML의 공고 ID가 다릅니다.")
        address = job.get("address") or {}
        location = " ".join(
            str(address[key]).strip()
            for key in ("location", "district") if address.get(key)
        )
        region_id = (region_ids or {}).get(location)
        if region_id is not None:
            region_id = str(UUID(region_id))
        career_type, minimum, maximum = _career_fields(job.get("career") or {})
        deadline_type, deadline_date = _deadline_fields(job, html)
        return WantedJobPost(
            id=str(uuid5(NAMESPACE_URL, url)),
            source_url=url,
            company_name=company,
            title=position,
            region_id=region_id,
            address=_text(address.get("full_location")),
            employment_type={"regular": "정규직", "contract": "계약직", "intern": "인턴"}.get(job.get("employment_type")),
            career_type=career_type,
            min_experience_months=minimum,
            max_experience_months=maximum,
            position_detail=_text(job.get("intro")),
            main_tasks=_text(job.get("main_tasks")),
            qualifications=_text(job.get("requirements")),
            preferred_qualifications=_text(job.get("preferred_points")),
            deadline_type=deadline_type,
            deadline_date=deadline_date,
            status={"active": "모집 중", "closed": "마감"}.get(job.get("status"), "미확인"),
        )
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise WantedCrawlError("공고 JSON을 읽을 수 없습니다. 공고 상태와 HTML 구조를 확인하세요.") from exc


def _fetch_html(url: str, timeout: float = 20) -> str:
    url = _canonical_url(url)
    request = Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html",
        "Accept-Language": "ko-KR,ko;q=0.9",
    })
    try:
        with urlopen(request, timeout=timeout) as response:
            html = response.read().decode(response.headers.get_content_charset() or "utf-8")
    except HTTPError as exc:
        raise WantedCrawlError(f"원티드 HTTP {exc.code}: 공고 삭제 또는 접근 제한을 확인하세요.") from exc
    except (URLError, TimeoutError) as exc:
        raise WantedCrawlError(f"원티드 연결 실패: {exc}") from exc
    return html


def crawl_wanted_job(url: str = DEFAULT_URL, *, timeout: float = 20, region_ids=None) -> WantedJobPost:
    """공개 원티드 공고 HTML을 한 번 요청해 수집합니다."""
    return parse_wanted_html(_fetch_html(url, timeout), url, region_ids=region_ids)


def collect_source(source: Path, *, html_dir=None, region_ids=None):
    """source.txt의 주석/빈 줄/중복을 제외하고 수집하며 실패를 개별 기록합니다."""
    urls = []
    for number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if line and not line.startswith("#"):
            try:
                urls.append(_canonical_url(line))
            except ValueError as exc:
                raise ValueError(f"{source}:{number}: {exc}") from exc
    counts = Counter(urls)
    results, checks, failures = [], [], []
    for url in counts:
        try:
            html = (
                (html_dir / f"{url.rsplit('/', 1)[-1]}.html").read_text(encoding="utf-8")
                if html_dir else _fetch_html(url)
            )
            job = parse_wanted_html(html, url, region_ids=region_ids)
            results.append(asdict(job))
            parser = _NextDataParser()
            parser.feed(html)
            raw = json.loads("".join(parser.parts))["props"]["pageProps"]["initialData"]
            checks.append({
                "source_url": url,
                "title": job.title,
                "null_fields": [k for k, v in asdict(job).items() if v is None],
                "source_region": " ".join(str(raw["address"].get(k) or "") for k in ("location", "district")).strip(),
                "source_due_time": raw.get("due_time"),
                "source_employment_type": raw.get("employment_type"),
                "source_status": raw.get("status"),
                "source_close_time": raw.get("close_time"),
                "warnings": [message for condition, message in [
                    (job.region_id is None, "지역 테이블 UUID 매핑 필요"),
                    (raw.get("close_time") and raw.get("status") == "active", "close_time 값이 있으나 status=active: 모집 상태는 원본 status 기준"),
                    (job.employment_type is None, "고용형태 누락 또는 미지원 코드"),
                    (job.status == "미확인", "모집 상태 누락 또는 미지원 코드"),
                    (job.career_type == "미확인", "경력 유형 확인 불가"),
                    (job.main_tasks is None, "주요업무 원문 없음"),
                    (job.qualifications is None, "자격요건 원문 없음"),
                    (job.preferred_qualifications is None, "우대사항 원문 없음"),
                ] if condition],
            })
        except (WantedCrawlError, ValueError, OSError) as exc:
            failures.append({"source_url": url, "error": str(exc)})
    return results, {
        "source_count": len(urls),
        "unique_count": len(counts),
        "duplicates": {url: count for url, count in counts.items() if count > 1},
        "success_count": len(results),
        "failure_count": len(failures),
        "null_field_counts": dict(Counter(k for job in results for k, v in job.items() if v is None)),
        "checks": checks,
        "failures": failures,
    }


def main():
    parser = argparse.ArgumentParser(description="원티드 공고를 JSON으로 출력합니다.")
    parser.add_argument("url", nargs="?", default=DEFAULT_URL)
    parser.add_argument("--html", type=Path, help="네트워크 요청 대신 저장된 HTML을 읽습니다.")
    parser.add_argument("--source", type=Path, help="공고 URL 목록 파일")
    parser.add_argument("--html-dir", type=Path, help="목록 검증용 HTML 폴더 (공고번호.html)")
    parser.add_argument("--regions", type=Path, help='지역명 → UUID JSON, 예: {"서울 강남구": "실제 UUID"}')
    parser.add_argument("--output", type=Path, help="추출 결과 JSON 저장 경로")
    parser.add_argument("--report", type=Path, help="목록 검증 결과 JSON 저장 경로")
    args = parser.parse_args()
    if args.html and args.source:
        parser.error("--html과 --source는 함께 사용할 수 없습니다.")
    if (args.html_dir or args.report) and not args.source:
        parser.error("--html-dir과 --report는 --source와 함께 사용하세요.")
    try:
        region_ids = json.loads(args.regions.read_text(encoding="utf-8")) if args.regions else None
        if region_ids is not None:
            if not isinstance(region_ids, dict):
                raise ValueError("지역 매핑은 JSON 객체여야 합니다.")
            for value in region_ids.values():
                UUID(value)
        report = None
        if args.source:
            result, report = collect_source(args.source, html_dir=args.html_dir, region_ids=region_ids)
        else:
            job = (
                parse_wanted_html(args.html.read_text(encoding="utf-8"), args.url, region_ids=region_ids)
                if args.html else crawl_wanted_job(args.url, region_ids=region_ids)
            )
            result = asdict(job)
        output = json.dumps(result, ensure_ascii=False, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output + "\n", encoding="utf-8")
        else:
            print(output)
        if report is not None:
            if args.report:
                args.report.parent.mkdir(parents=True, exist_ok=True)
                args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            import sys
            print(f"목록 {report['source_count']}개 / 고유 {report['unique_count']}개 / 성공 {report['success_count']}개 / 실패 {report['failure_count']}개", file=sys.stderr)
            if report["failure_count"]:
                parser.exit(1)
    except (WantedCrawlError, ValueError, OSError) as exc:
        parser.exit(1, f"크롤링 실패: {exc}\n")


if __name__ == "__main__":
    main()
