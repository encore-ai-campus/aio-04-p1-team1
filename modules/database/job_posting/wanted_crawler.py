"""원티드 상세 HTML을 이 패키지의 JobPosting 모델로 직접 변환합니다."""
import json
import re
from datetime import datetime
from html.parser import HTMLParser
from urllib.parse import urlsplit

from .schemas import JobPosting


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
    return career_type, start if start is not None else None, (
        end if end is not None and end != 100 else None
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


def next_data(html):
    parser = _NextDataParser()
    parser.feed(html)
    if not parser.parts:
        raise WantedCrawlError('__NEXT_DATA__가 없습니다. 차단 응답 또는 HTML 구조를 확인하세요.')
    try:
        return json.loads(''.join(parser.parts))['props']['pageProps']
    except (ValueError, KeyError, TypeError) as exc:
        raise WantedCrawlError('공고 JSON을 읽을 수 없습니다.') from exc


def parse_job(html, url, job_name):
    url = _canonical_url(url)
    try:
        raw = next_data(html)['initialData']
        if not isinstance(raw, dict) or not isinstance(raw.get('company'), dict):
            raise ValueError('공고 데이터가 없습니다.')
        company = _text(raw['company']['company_name'])
        title = _text(raw['position'])
        if not company or not title:
            raise ValueError('회사명 또는 공고 제목이 없습니다.')
        if str(raw.get('id')) != url.rsplit('/', 1)[-1]:
            raise ValueError('요청 URL과 공고 ID가 다릅니다.')
        career_type, minimum, maximum = _career_fields(raw.get('career') or {})
        deadline_type, deadline_date = _deadline_fields(raw, html)
        address = raw.get('address') or {}
        region = ' '.join(str(address[k]).strip() for k in ('location', 'district') if address.get(k))
        # 해외 공고는 시·도 필드 없이 상세 주소에만 실제 근무지가 제공되기도 합니다.
        if not region and isinstance(address.get('full_location'), str):
            region = address['full_location'].strip()
        if not region:
            raise ValueError('원본에 대표 근무 지역이 없어 필수 region_name을 채울 수 없습니다.')
        return JobPosting(
            source_url=url, title=title, company_name=company,
            job_name=job_name, region_name=region,
            employment_type={'regular': '정규직', 'contract': '계약직', 'intern': '인턴'}.get(raw.get('employment_type')),
            career_type=career_type, min_experience_years=minimum,
            max_experience_years=None if career_type == '신입' else maximum,
            position_detail=_text(raw.get('intro')), main_tasks=_text(raw.get('main_tasks')),
            qualifications=_text(raw.get('requirements')), preferred_qualifications=_text(raw.get('preferred_points')),
            deadline_type=deadline_type, deadline_date=deadline_date,
            use_yn='N' if raw.get('status') == 'closed' else 'Y',
        )
    except (KeyError, TypeError, AttributeError) as exc:
        raise WantedCrawlError('공고 JSON 구조가 올바르지 않습니다.') from exc
