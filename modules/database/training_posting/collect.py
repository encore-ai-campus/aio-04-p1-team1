"""8개 직무별 목표 충족 시 조회를 멈추는 훈련과정 수집기."""

import argparse
import hashlib
import json
import random
import re
import sys
import time
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo

from modules.database.training_posting.schemas import TrainingPosting
from modules.database.training_posting.work24_client import (
    MODULE_DIR, Work24APIError, build_search_params, load_api_key,
    parse_training_xml, search_training_courses,
)

# 사용자 지정 주제와 띄어쓰기/영문 표기 변형. 포괄 검색어도 제목 관련성 검증을 통과해야 합니다.
JOB_RULES = {
    '개발자': ['백엔드', '프론트엔드', '웹개발', 'Java', 'Spring', 'React', '소프트웨어 개발'],
    '데이터 분석가': ['데이터 분석', 'SQL', 'Python 분석', '통계', '시각화', 'Power BI'],
    '인사': ['인사관리', '채용', '노무', '급여', '조직관리'],
    '총무': ['총무실무', '자산관리', '구매관리', '사무행정'],
    '회계': ['재무회계', '세무회계', '전산회계', '전산세무', '결산'],
    '생산관리': ['생산계획', '공정관리', '품질관리', '재고관리', 'SCM', '생산 ERP'],
    '마케팅': ['디지털 마케팅', '퍼포먼스 마케팅', '콘텐츠 마케팅', '광고', 'CRM'],
    '기획자': ['서비스기획', '사업기획', '상품기획', '시장조사', '요구사항 정의'],
}
SEARCH_ALIASES = {
    '개발자': ['웹 개발', '자바', '소프트웨어개발'],
    '데이터 분석가': ['데이터분석', '파이썬', '데이터', '파워비아이'],
    '인사': ['인사', '인사 관리', 'HR'],
    '총무': ['총무', '구매', '사무 행정'],
    '회계': ['회계', '세무'],
    '생산관리': ['생산관리', '생산 관리', '품질', 'ERP', 'ERP생산', '생산', '물류관리', '자재관리', '공급망'],
    '마케팅': ['마케팅', '디지털마케팅', '퍼포먼스마케팅', '콘텐츠마케팅'],
    '기획자': ['기획', '서비스 기획', '사업 기획', '상품 기획', '시장 조사', '시장분석', '요구사항', '비즈니스모델', '사업계획서', '사업전략', '경영전략', '사업타당성', '사업성분석', '신사업', '마케팅조사', '시장리서치', '고객분석', '고객조사', '상품전략', '제품전략', '서비스전략', '경쟁사분석'],
}
MATCH_ALIASES = {
    '개발자': ['자바', '프론트엔드', '프론트엔드개발', '백엔드', '소프트웨어개발'],
    '데이터 분석가': ['데이터분석', '파이썬데이터', 'python데이터', '파이썬분석', '파워비아이', 'sqld'],
    '인사': ['인사실무', '인사노무', '인적자원관리', '인사담당', '인사급여', '인사평가', '인사행정', '인사회계', '인사경리', 'HRM'],
    '총무': ['총무', '구매실무', '구매담당'],
    '회계': ['회계실무', '세무실무', '회계관리', '회계원리', '재무제표'],
    '생산관리': ['생산관리', '생산실무', '품질경영', 'ERP생산', '물류관리', '자재관리', '공급망', '생산정보관리', '생산시스템', '생산운영', '생산공정'],
    '마케팅': ['마케팅', '브랜딩'],
    '기획자': ['서비스기획', '사업기획', '상품기획', '제품기획', '전략기획', '경영기획', '기획실무', '비즈니스모델', '사업계획서', '사업전략', '경영전략', '사업타당성', '사업성분석', '신사업', '시장분석', '마케팅조사', '마케팅리서치', '시장리서치', '고객분석', '고객데이터분석', '고객조사', '상품전략', '제품전략', '서비스전략', '경쟁사분석', '요구사항분석', '요구사항관리', '기획서', '기획력', '기획보고', '기획전략'],
}


def _normalize(value):
    return re.sub(r'[^a-z0-9가-힣]', '', value.casefold())


def match_jobs(title):
    text = _normalize(title)
    evidence = {}
    for role, keywords in JOB_RULES.items():
        matched = [term for term in keywords + MATCH_ALIASES[role] if _normalize(term) in text]
        if role == '인사' and '인사' in text and any(word in text for word in ['erp', '정보관리사']):
            matched.append('ERP 인사')
        if role == '생산관리' and '생산' in text and any(word in text for word in ['erp', '정보관리사']):
            matched.append('ERP 생산')
        # 금융 자산관리는 사무/총무 자산관리 교육과 분리합니다.
        if role == '총무' and any(word in text for word in ['부동산', '금융투자', '펀드', '자산운용']):
            matched = []
        # 영상 제작만을 다루는 과정은 마케팅 관련 표현이 추가로 있어야 합니다.
        if role == '마케팅' and any(word in text for word in ['영상편집', '영상제작', '모션그래픽']):
            if not any(word in text for word in ['마케팅', '퍼포먼스', 'crm']):
                matched = []
        if role == '기획자' and any(word in text for word in ['영상편집', '영상제작', '모션그래픽']):
            if not any(word in text for word in ['서비스기획', '사업기획', '상품기획', '경영기획', '요구사항']):
                matched = []
        if matched:
            evidence[role] = sorted(set(matched))
    return evidence


def _date(value):
    if not value or not value.strip():
        return None
    value = value.strip()
    for pattern in ('%Y-%m-%d', '%Y%m%d', '%Y.%m.%d'):
        try:
            return datetime.strptime(value, pattern).date().isoformat()
        except ValueError:
            pass
    raise ValueError('invalid_training_date')


def normalize_course(raw):
    course_id, title, url = (raw.get(key, '').strip() for key in ('trprId', 'title', 'titleLink'))
    if not course_id or not title or not url:
        raise ValueError('missing_required_field')
    parsed = urlsplit(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname:
        raise ValueError('invalid_source_url')
    start, end = _date(raw.get('traStartDate')), _date(raw.get('traEndDate'))
    if start and end and start > end:
        raise ValueError('invalid_date_range')
    return asdict(TrainingPosting(
        training_id=course_id, source_url=url, title=title,
        center_name=raw.get('subTitle', '').strip() or None,
        center_address=raw.get('address', '').strip() or None,
        training_start_dt=start, training_end_dt=end,
    ))


def assign_jobs(pool, quota=125, seed=42, preferred=None):
    """교차 직무 과정은 한 곳에 배정하고, 대체 가능한 과정을 재배정해 부족 직무를 채웁니다."""
    rng = random.Random(seed)
    eligible = {role: [key for key, item in pool.items() if role in item['matches']] for role in JOB_RULES}
    for role, values in eligible.items():
        rng.shuffle(values)
        # 재개할 때 기존 선정 결과를 우선해 불필요한 교체를 줄입니다.
        previous = set((preferred or {}).get(role, []))
        values.sort(key=lambda key: key not in previous)
    owner = {}
    selected = {role: set() for role in JOB_RULES}

    def acquire(role, visited):
        if role in visited:
            return False
        visited.add(role)
        for key in eligible[role]:
            previous = owner.get(key)
            if previous == role:
                continue
            if previous is None or acquire(previous, visited):
                if previous is not None:
                    selected[previous].remove(key)
                owner[key] = role
                selected[role].add(key)
                return True
        return False

    # 후보가 적은 직무부터 한 건씩 균등하게 채웁니다.
    roles = sorted(JOB_RULES, key=lambda role: len(eligible[role]))
    for _ in range(quota):
        for role in roles:
            acquire(role, set())
    return {role: sorted(keys) for role, keys in selected.items()}


def preload_cache(output_dir, start, end):
    """동일 기간의 이전 검색 응답을 API 호출 없이 다시 분류합니다."""
    report_file = output_dir / 'validation_report.json'
    if not report_file.exists():
        return {}, {}
    previous = json.loads(report_file.read_text(encoding='utf-8'))
    if previous.get('date_range') != {'start': start, 'end': end}:
        return {}, {}
    pool = {}
    for query in previous.get('queries', []):
        conditions = dict(keyword=query['keyword'], start=start, end=end, page=query['page'], page_size=100)
        fingerprint = hashlib.sha256(json.dumps(conditions, sort_keys=True).encode()).hexdigest()[:20]
        path = output_dir / 'api_cache' / f'{fingerprint}.xml'
        if not path.exists():
            continue
        for raw in parse_training_xml(path.read_text(encoding='utf-8')).courses:
            try:
                row = normalize_course(raw)
            except ValueError:
                continue
            matches = match_jobs(row['title'])
            if not matches:
                continue
            key = row['training_id']
            if key not in pool or (row['training_start_dt'] or '9999') < (pool[key]['record']['training_start_dt'] or '9999'):
                pool[key] = dict(record=row, matches=matches, raw=raw)
    return pool, previous


def collect(*, api_key, start, end, quota=125, max_calls=160, seed=42,
            interval=0.25, output_dir=None, resume=False, fetch=None, progress=None):
    if quota < 1 or max_calls < 1 or interval < 0:
        raise ValueError('quota/max_calls는 양수, interval은 0 이상이어야 합니다.')
    build_search_params(keyword='', start=start, end=end)
    fetch = fetch or (lambda **kw: search_training_courses(api_key, **kw))
    pool, rejects, requests, errors = {}, Counter(), [], []
    cache = {}
    queues = {role: [(term, 1) for term in dict.fromkeys(JOB_RULES[role] + SEARCH_ALIASES[role])] for role in JOB_RULES}
    raw_rows = network_calls = cache_hits = 0
    output_dir = Path(output_dir) if output_dir else None
    previous = {}
    if output_dir:
        (output_dir / 'api_cache').mkdir(parents=True, exist_ok=True)
        if resume:
            pool, previous = preload_cache(output_dir, start, end)
    preferred = {role: [row['training_id'] for row in previous.get('selection', []) if row['job'] == role] for role in JOB_RULES}
    assignment = assign_jobs(pool, quota, seed, preferred)
    requests.extend(previous.get('queries', []))
    while any(queues.values()) and network_calls < max_calls:
        changed = False
        for role in JOB_RULES:
            if len(assignment[role]) >= quota or not queues[role]:
                continue
            keyword, page = queues[role].pop(0)
            conditions = dict(keyword=keyword, start=start, end=end, page=page, page_size=100)
            fingerprint = hashlib.sha256(json.dumps(conditions, sort_keys=True).encode()).hexdigest()[:20]
            cache_file = output_dir / 'api_cache' / f'{fingerprint}.xml' if output_dir else None
            try:
                if fingerprint in cache:
                    result, raw, params = cache[fingerprint]
                    cache_hits += 1
                elif resume and cache_file and cache_file.exists():
                    raw = cache_file.read_text(encoding='utf-8')
                    result, params = parse_training_xml(raw), build_search_params(**conditions)
                    cache[fingerprint] = (result, raw, params)
                    cache_hits += 1
                else:
                    if network_calls >= max_calls:
                        break
                    if network_calls and interval:
                        time.sleep(interval)
                    network_calls += 1
                    result, raw, params = fetch(**conditions)
                    cache[fingerprint] = (result, raw, params)
                    if cache_file:
                        cache_file.write_text(raw, encoding='utf-8')
                raw_rows += len(result.courses)
                new_count = 0
                for course in result.courses:
                    try:
                        row = normalize_course(course)
                    except ValueError as exc:
                        rejects[str(exc)] += 1
                        continue
                    matches = match_jobs(row['title'])
                    if not matches:
                        rejects['no_job_title_match'] += 1
                        continue
                    key = row['training_id']
                    if key in pool:
                        rejects['duplicate_course_id'] += 1
                        # 가장 가까운 시작일의 회차를 남깁니다.
                        if (row['training_start_dt'] or '9999') < (pool[key]['record']['training_start_dt'] or '9999'):
                            pool[key] = dict(record=row, matches=matches, raw=course)
                        continue
                    if any(item['record']['source_url'] == row['source_url'] for item in pool.values()):
                        rejects['duplicate_source_url'] += 1
                        continue
                    pool[key] = dict(record=row, matches=matches, raw=course)
                    new_count += 1
                assignment = assign_jobs(pool, quota, seed, preferred)
                if not any(q['keyword'] == keyword and q['page'] == page for q in requests):
                    requests.append(dict(role=role, keyword=keyword, page=page, total_count=result.total_count,
                                         received=len(result.courses), new_unique_courses=new_count))
                # 먼저 다른 검색어를 확인하고 다음 페이지는 대기열 뒤에 넣습니다.
                if page < min(1000, (result.total_count + 99) // 100) and result.courses:
                    queues[role].append((keyword, page + 1))
                changed = True
                if progress:
                    progress(network_calls, {name: len(keys) for name, keys in assignment.items()})
            except Work24APIError as exc:
                errors.append(dict(role=role, keyword=keyword, page=page, error=str(exc)))
                if output_dir and exc.response_xml:
                    (output_dir / 'training_error.xml').write_text(exc.response_xml, encoding='utf-8')
                queues = {name: [] for name in JOB_RULES}
                break
        if not changed or all(len(keys) >= quota for keys in assignment.values()):
            break
    selected_ids = [key for role in JOB_RULES for key in assignment[role]]
    records = [pool[key]['record'] for key in selected_ids]
    full = all(len(keys) >= quota for keys in assignment.values())
    report = {
        'status': 'complete' if full else 'failed' if errors and not records else 'partial',
        'stop_reason': 'quota_reached' if full else 'api_error' if errors else 'call_limit' if network_calls >= max_calls else 'search_plan_exhausted',
        'date_range': {'start': start, 'end': end}, 'quota_per_job': quota, 'target_total': quota * len(JOB_RULES),
        'selected_total': len(records), 'unique_candidates': len(pool), 'api_calls': network_calls,
        'cache_hits': cache_hits, 'processed_response_rows': raw_rows, 'max_api_calls': max_calls, 'seed': seed,
        'api_calls_previous_runs': previous.get('api_calls_all_runs', previous.get('api_calls', 0)),
        'api_calls_all_runs': previous.get('api_calls_all_runs', previous.get('api_calls', 0)) + network_calls,
        'preflight_api_calls': previous.get('preflight_api_calls', 0),
        'api_calls_including_preflight': previous.get('api_calls_all_runs', previous.get('api_calls', 0)) + network_calls + previous.get('preflight_api_calls', 0),
        'search_rules': JOB_RULES, 'search_aliases': SEARCH_ALIASES, 'matching_aliases': MATCH_ALIASES,
        'classification_policy': '제목 키워드/표기 변형 일치, 과정 ID당 한 회차, 대표 직무 한 개',
        'job_counts': {role: len(keys) for role, keys in assignment.items()},
        'shortages': {role: quota - len(keys) for role, keys in assignment.items() if len(keys) < quota},
        'rejected_counts': dict(rejects), 'queries': requests, 'errors': errors,
        'selection': [{
            'training_id': key, 'job': role, 'title': pool[key]['record']['title'],
            'matching_evidence': pool[key]['matches'][role],
            'related_jobs': list(pool[key]['matches']), 'source_url': pool[key]['record']['source_url'],
        } for role in JOB_RULES for key in assignment[role]],
        'center_counts': dict(Counter(row['center_name'] or '미확인' for row in records)),
        'database': {'status': 'not_saved'},
    }
    return records, report


def write_outputs(directory, records, report):
    directory.mkdir(parents=True, exist_ok=True)
    for name, value in [('training_postings.json', records), ('validation_report.json', report)]:
        path = directory / name
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        temporary.replace(path)


def main():
    today = datetime.now(ZoneInfo('Asia/Seoul')).date()
    parser = argparse.ArgumentParser(description='8개 직무별 훈련과정 수집 및 저장')
    parser.add_argument('--start', default=today.strftime('%Y%m%d'))
    parser.add_argument('--end', default=(today + timedelta(days=181)).strftime('%Y%m%d'))
    parser.add_argument('--quota', type=int, default=125)
    parser.add_argument('--max-calls', type=int, default=160)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--interval', type=float, default=0.25)
    parser.add_argument('--output-dir', type=Path, default=MODULE_DIR / 'results')
    parser.add_argument('--resume', action='store_true', help='같은 조건의 성공 XML 캐시를 재사용')
    parser.add_argument('--save-db', action='store_true')
    args = parser.parse_args()
    try:
        def progress(calls, counts):
            print(json.dumps({'api_calls': calls, 'job_counts': counts}, ensure_ascii=False), file=sys.stderr, flush=True)
        records, report = collect(api_key=load_api_key(), start=args.start, end=args.end, quota=args.quota,
            max_calls=args.max_calls, seed=args.seed, interval=args.interval, output_dir=args.output_dir,
            resume=args.resume, progress=progress)
        write_outputs(args.output_dir, records, report)
        if args.save_db:
            from modules.database.training_posting.save_to_supabase import save_records, load_database_url
            try:
                records, summary = save_records(records, load_database_url())
                report['database'] = dict(status='saved', **summary)
            except Exception as exc:
                report['database'] = dict(status='failed', error_type=type(exc).__name__, sqlstate=getattr(exc, 'sqlstate', None))
                write_outputs(args.output_dir, records, report)
                parser.exit(1, 'Supabase 저장 실패. validation_report.json을 확인하세요.\n')
        write_outputs(args.output_dir, records, report)
        print(json.dumps({name: report[name] for name in ('status', 'selected_total', 'api_calls', 'job_counts', 'shortages', 'database')}, ensure_ascii=False, indent=2))
        if report['status'] != 'complete':
            parser.exit(1 if report['errors'] else 2)
    except (Work24APIError, ValueError, OSError) as exc:
        parser.exit(1, f'수집 실패: {exc}\n')


if __name__ == '__main__':
    main()
