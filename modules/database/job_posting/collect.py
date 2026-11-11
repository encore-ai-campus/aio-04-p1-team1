"""원티드 링크 검색·전체/샘플 수집·저장 없는 3건 확인의 통합 실행 파일.

검색 결과 제목 또는 원티드 직무 태그를 검증합니다. API 페이지 크기는 20입니다.
"""
import argparse
import csv
import shutil
from collections import Counter
import re
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

import httpx
from .wanted_crawler import parse_job, _canonical_url

MODULE_DIR = Path(__file__).resolve().parent
BASE = 'https://www.wanted.co.kr'
RULES = {
    '개발자': {'queries': ['개발자', 'Developer', '소프트웨어 엔지니어'], 'pattern': r'개발|developer|software|engineer|엔지니어', 'parents': [518], 'tags': []},
    '데이터 분석가': {'queries': ['데이터 분석가', '데이터 분석', 'Data Analyst', '데이터분석'], 'pattern': r'데이터\s*분석|data\s*analyst|비즈니스\s*분석|BI\s*분석', 'parents': [], 'tags': [656]},
    '인사': {'queries': ['인사', 'HR', 'People'], 'pattern': r'인사|채용|노무|HR|human\s*resource|people|recruit|talent', 'parents': [], 'tags': [643]},
    '총무': {'queries': ['총무', 'General Affairs', '오피스 매니저'], 'pattern': r'총무|general\s*affairs|\bGA\b|오피스\s*매니저|office\s*manager', 'parents': [], 'tags': [562]},
    '회계': {'queries': ['회계', 'Accountant'], 'pattern': r'회계|경리|세무|accountant|accounting', 'parents': [], 'tags': [1034, 534, 542]},
    '생산관리': {'queries': ['생산관리', '생산 관리', 'Production Manager', '생산계획'], 'pattern': r'생산\s*관리|생산\s*계획|production\s*(manager|management|plan)', 'parents': [], 'tags': [701]},
    '마케팅': {'queries': ['마케팅', '마케터', 'Marketing'], 'pattern': r'마케팅|마케터|marketing|marketer', 'parents': [523], 'tags': []},
    '기획자': {'queries': ['기획자', '서비스 기획', '사업 기획', '상품 기획', '전략 기획'], 'pattern': r'기획|product\s*(manager|owner)|\bPM\b|\bPO\b|planner', 'parents': [], 'tags': [564,565,563,10232]},
}


def write_search_report(report):
    path = MODULE_DIR / 'results/search_report.txt'
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ['직무별 링크 수집 결과', '제목 또는 원티드 직무 태그로 관련성을 확인하고 직무 간 중복 URL을 제거합니다.', '']
    for role, info in report.items():
        lines.extend([f"{role}: {info['links']}개", f"검색어: {', '.join(q['query'] for q in info['queries'])}"])
        for query in info['queries']:
            lines.append(f"  {query['query']}: 검색 응답 총수 {query['reported_total']}, {query['pages']}페이지, 조회 {query['received']}건, 끝까지 조회 {query['exhausted']}")
        lines.append('')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def write_validation_report(report):
    path = MODULE_DIR / 'results/validation_report.txt'
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"수집 시각: {report['generated_at']}", f"직무별 상세 수집 상한: {report['per_job']}", f"수집 행 수: {report['total_rows']}", '']
    for role, info in report['roles'].items():
        lines.append(f"{role}: 링크 {info['source_links']}개, 선택 {info['selected']}개, 수집 {info['crawled']}개")
    lines.extend(['', '원본에서 수집하지 못한 항목(NULL) 건수:'])
    lines.extend(f'  {key}: {count}' for key, count in report['missing_fields'].items() if count)
    lines.extend(['', '마감 날짜 누락 공고:'])
    lines.extend(report['date_only_deadlines'] or ['없음'])
    lines.extend(['', '수집 오류:'])
    lines.extend(str(error) for error in report['errors'])
    if not report['errors']:
        lines.append('없음')
    lines.extend(['', 'DB 저장 결과:'])
    if report.get('database'):
        lines.extend(f'  {key}: {value}' for key, value in report['database'].items())
    else:
        lines.append('아직 저장하지 않음')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def write_records(records):
    if not records:
        raise ValueError('수집한 공고가 없습니다.')
    path = MODULE_DIR / 'results/job_postings.csv'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def relevant(item, role):
    rule = RULES[role]
    tag = item.get('category_tag') or {}
    return bool(re.search(rule['pattern'], item.get('position', ''), re.I)
                or tag.get('id') in rule['tags'] or tag.get('parent_id') in rule['parents'])


def fetch(client, url, *, params=None):
    # 공개 API의 정상 리디렉션을 따릅니다. 로그인 정보는 보내지 않습니다.
    for attempt in range(3):
        try:
            response = client.get(url, params=params)
            response.raise_for_status()
            return response
        except (httpx.TimeoutException, httpx.NetworkError):
            if attempt == 2:
                raise
            time.sleep(attempt + 1)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))


def collect_links(client, limit=100):
    report, sources, global_seen = {}, {}, set()
    for role, rule in RULES.items():
        picked, queries, rejected = [], [], 0
        for query in rule['queries']:
            if len(picked) >= limit:
                break
            params = {'query': query, 'limit': 20, 'offset': 0}
            seen_pages = set()
            pages, received, total, complete = 0, 0, None, False
            while len(picked) < limit:
                fingerprint = tuple(sorted(params.items()))
                if fingerprint in seen_pages:
                    raise RuntimeError('같은 검색 페이지가 반복되어 수집을 중단합니다.')
                seen_pages.add(fingerprint)
                data = fetch(client, BASE + '/api/chaos/search/v1/position/', params=params).json()
                pages += 1
                total = data.get('total_count')
                items = data.get('data')
                if not isinstance(items, list):
                    raise ValueError('검색 응답 data가 배열이 아닙니다.')
                received += len(items)
                for item in items:
                    url = _canonical_url(f"{BASE}/wd/{item['id']}")
                    if not relevant(item, role):
                        rejected += 1
                        continue
                    if url not in global_seen:
                        picked.append(url)
                        global_seen.add(url)
                    if len(picked) == limit:
                        break
                next_link = (data.get('links') or {}).get('next')
                if not items or not next_link:
                    complete = True
                    break
                params = dict(parse_qsl(urlsplit(next_link).query))
                params['limit'] = 20
                time.sleep(0.15)
            queries.append({'query': query, 'reported_total': total, 'pages': pages,
                            'received': received, 'exhausted': complete})
        sources[role] = picked
        report[role] = {'links': len(picked), 'below_target': len(picked) < limit,
                        'rejected_unrelated': rejected, 'queries': queries}
        print(f'{role}: 링크 {len(picked)}개', flush=True)
        # 중간 진행 결과도 보존합니다. 검색 실패 시 완료로 표시하지 않습니다.
        write_search_report(report)
    (MODULE_DIR / 'source.txt').write_text('\n\n\n'.join(
        '## ' + role + '\n' + '\n'.join(urls) for role, urls in sources.items()) + '\n', encoding='utf-8')
    return report


def read_sources(path):
    groups, current, seen = {}, None, set()
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('## '):
            current = line[3:].strip()
            if current not in RULES or current in groups:
                raise ValueError('source.txt 직무 헤더가 알맞지 않거나 중복되었습니다.')
            groups[current] = []
        else:
            if current is None:
                raise ValueError('URL보다 먼저 직무 헤더가 필요합니다.')
            url = _canonical_url(line)
            if url in seen:
                raise ValueError('source.txt에 중복 URL이 있습니다.')
            seen.add(url)
            groups[current].append(url)
    if set(groups) != set(RULES):
        raise ValueError('source.txt에 8개 직무 헤더가 모두 있어야 합니다.')
    return groups


def crawl_samples(client, per_job=10):
    groups = read_sources(MODULE_DIR / 'source.txt')
    records, errors, checks = [], [], {}
    for role, urls in groups.items():
        selected = urls[:per_job]
        done = 0
        for url in selected:
            try:
                # HTML은 메모리에서만 파싱합니다. DB 저장 재시도에는 결과 CSV를 사용합니다.
                html = fetch(client, url).text
                time.sleep(0.15)
                record = asdict(parse_job(html, url, role))
                records.append(record)
                done += 1
            except (ValueError, RuntimeError, httpx.HTTPError) as exc:
                # DB 연결/비밀키를 예외에 포함하지 않습니다.
                errors.append({'job_name': role, 'source_url': url, 'error': type(exc).__name__, 'reason': str(exc)[:300]})
        checks[role] = {'source_links': len(urls), 'selected': len(selected), 'crawled': done}
        print(f'{role}: 상세 {done}/{len(selected)}개', flush=True)
    report = {'generated_at': datetime.now(timezone.utc).isoformat(), 'per_job': per_job,
              'roles': checks, 'total_rows': len(records), 'errors': errors,
              'missing_fields': {key: sum(row[key] is None for row in records) for key in records[0] if key != 'id'} if records else {},
              'date_only_deadlines': [], 'database': None}
    # 날짜 지정 공고에서 날짜를 수집하지 못한 경우 따로 보고합니다.
    for record in records:
        if record['deadline_type'] == '날짜 지정' and record['deadline_date'] is None:
            report['date_only_deadlines'].append(record['source_url'])
    write_records(records)
    write_validation_report(report)
    return records, report


def read_saved(database_url, urls):
    from .save_to_supabase import verify_schema, validate_records
    import psycopg
    from psycopg.rows import dict_row
    with psycopg.connect(database_url, sslmode='require', connect_timeout=15, row_factory=dict_row) as connection:
        if not connection.execute("SELECT to_regclass('public.job_postings') IS NOT NULL AS yes").fetchone()['yes']:
            return {}  # 최초 전체 수집에서는 첫 저장 묶음이 테이블을 생성합니다.
        verify_schema(connection)
        rows = connection.execute('SELECT * FROM public.job_postings WHERE source_url=ANY(%s)', (urls,)).fetchall()
    result = {}
    for row in rows:
        row['id'] = str(row['id'])
        if row['deadline_date'] is not None:
            row['deadline_date'] = row['deadline_date'].isoformat()
        validate_records([row])
        result[row['source_url']] = row
    return result


def collect_all():
    """전체 링크 중 미저장 공고를 20개씩 저장하고 최종 DB 값을 비교합니다."""
    from .save_to_supabase import load_database_url, save_records, validate_records
    groups = read_sources(MODULE_DIR / 'source.txt')
    urls = [url for items in groups.values() for url in items]
    role_for_url = {url: role for role, items in groups.items() for url in items}
    database_url = load_database_url()
    saved = read_saved(database_url, urls)
    for url, row in saved.items():
        if row['job_name'] != role_for_url[url]:
            raise RuntimeError('기존 DB 직무와 source.txt 직무가 달라 수집을 중단합니다.')
    initial = set(saved)
    print(f'입력 {len(urls)}개 / 기존 저장 {len(initial)}개 / 추가 수집 {len(urls)-len(initial)}개', flush=True)
    backup = MODULE_DIR / 'results/backups' / datetime.now().strftime('%Y%m%d_%H%M%S_full')
    backup.mkdir(parents=True, exist_ok=True)
    for name in ('job_postings.csv', 'validation_report.txt'):
        path = MODULE_DIR / 'results' / name
        if path.exists():
            shutil.copy2(path, backup / name)
    errors, pending = [], []

    def checkpoint(final=False):
        nonlocal pending
        if pending:
            records, _ = save_records(pending, database_url)
            saved.update({row['source_url']: row for row in records})
            pending = []
        ordered = [saved[url] for url in urls if url in saved]
        if not ordered:
            return
        report = {
            'generated_at': datetime.now(timezone.utc).isoformat(), 'per_job': '전체 링크',
            'roles': {role: {'source_links': len(items), 'selected': len(items),
                             'crawled': sum(url in saved for url in items)} for role, items in groups.items()},
            'total_rows': len(ordered), 'errors': errors,
            'missing_fields': {key: sum(row[key] is None for row in ordered) for key in ordered[0] if key != 'id'},
            'date_only_deadlines': [row['source_url'] for row in ordered if row['deadline_type']=='날짜 지정' and not row['deadline_date']],
            'database': {'table': 'public.job_postings', 'verified_rows': len(ordered),
                         'previously_saved': len(initial), 'newly_saved': len(set(saved)-initial),
                         'remaining_urls': len(urls)-len(saved), 'complete': final and len(saved)==len(urls),
                         'counts_by_job': dict(Counter(row['job_name'] for row in ordered)),
                         'deadline_date_type': 'date',
                         'newbie_max_nonnull': sum(row['career_type']=='신입' and row['max_experience_years'] is not None for row in ordered)},
        }
        write_records(ordered)
        write_validation_report(report)
        print(f'저장·검증 {len(saved)}/{len(urls)}개 (추가 {len(set(saved)-initial)}개, 오류 {len(errors)}개)', flush=True)

    with httpx.Client(timeout=25, follow_redirects=True) as client:
        for role, items in groups.items():
            for url in items:
                if url in saved:
                    continue
                try:
                    html = fetch(client, url).text
                    row = asdict(parse_job(html, url, role))
                    validate_records([row])
                    pending.append(row)
                except (ValueError, RuntimeError, httpx.HTTPError) as exc:
                    errors.append({'job_name': role, 'source_url': url, 'error': type(exc).__name__, 'reason': str(exc)[:250]})
                    print(f'수집 오류: {role} {url} {type(exc).__name__}', flush=True)
                if len(pending) >= 20:
                    checkpoint()
                time.sleep(0.15)
            checkpoint()
            print(f'{role}: 저장 {sum(url in saved for url in items)}/{len(items)}개', flush=True)
    # 커밋 이후 실제 DB 값을 다시 읽어 전체 저장 건수 및 값을 비교합니다.
    actual = read_saved(database_url, urls)
    if actual != saved:
        raise RuntimeError('최종 DB 값 비교가 일치하지 않습니다.')
    checkpoint(final=True)
    if errors or len(saved) != len(urls):
        raise RuntimeError('일부 공고가 미수집 상태입니다. 검증 보고서를 확인하고 같은 명령으로 재시도하세요.')
    print(f'전체 완료: {len(saved)}개, 신규 {len(set(saved)-initial)}개', flush=True)


def check_collection():
    """실제 공고 3건을 메모리에서만 검증합니다. 결과 파일과 DB에 저장하지 않습니다."""
    from .save_to_supabase import validate_records
    groups = read_sources(MODULE_DIR / 'source.txt')
    selections = [(role, groups[role][0]) for role in ('개발자', '데이터 분석가')]
    overseas = 'https://www.wanted.co.kr/wd/396312'
    selections.append(('생산관리', overseas if overseas in groups['생산관리'] else groups['생산관리'][0]))
    with httpx.Client(timeout=25, follow_redirects=True) as client:
        for role, url in selections:
            row = asdict(parse_job(fetch(client, url).text, url, role))
            validate_records([row])
            print(f"수집 성공: {role} / {row['title']} / {row['region_name']}", flush=True)
    print('3/3건 수집·검증 완료. 결과 파일·DB 저장 없음.', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--links-only', action='store_true')
    modes.add_argument('--all', action='store_true', help='기존 source.txt 전체 중 미저장 공고를 20개씩 저장 (--save 필요)')
    modes.add_argument('--check', action='store_true', help='실제 공고 3건을 확인만 함. 파일·DB 저장 없음')
    modes.add_argument('--samples-only', action='store_true')
    parser.add_argument('--per-job', type=int, default=10)
    parser.add_argument('--link-limit', type=int, default=100)
    parser.add_argument('--replace', action='store_true', help='재수집한 URL의 기존 행을 삭제 후 교체 (--save 필요)')
    parser.add_argument('--save', action='store_true', help='상세 수집 후 Supabase public.job_postings에 저장')
    args = parser.parse_args()
    if args.all and (not args.save or args.replace):
        parser.error('--all은 --save와 함께 사용하고 --replace는 사용할 수 없습니다.')
    if args.check and (args.save or args.replace):
        parser.error('--check는 --save/--replace와 함께 사용할 수 없습니다.')
    if args.replace and not args.save:
        parser.error('--replace는 --save와 함께 사용하세요.')
    if args.links_only and args.save:
        parser.error('--links-only는 --save와 함께 사용할 수 없습니다.')
    if args.links_only and args.samples_only:
        parser.error('실행 모드는 하나만 선택하세요.')
    if not 1 <= args.per_job <= 100 or not 1 <= args.link_limit <= 100:
        parser.error('직무별 건수는 1~100 사이여야 합니다.')
    if args.all:
        collect_all()
        return
    if args.check:
        check_collection()
        return
    with httpx.Client(timeout=25, follow_redirects=True) as client:
        if not args.samples_only:
            collect_links(client, args.link_limit)
        if not args.links_only:
            records, report = crawl_samples(client, args.per_job)
            if args.save:
                if report['errors']:
                    raise RuntimeError('상세 수집 오류가 있어 DB 저장을 중단합니다. validation_report.txt를 확인하세요.')
                from .save_to_supabase import save_records, load_database_url
                saved, summary = save_records(records, load_database_url(), replace=args.replace)
                write_records(saved)
                report['database'] = summary
                write_validation_report(report)
                print(f"public.job_postings 저장·검증 완료: {summary['verified_rows']}개", flush=True)

if __name__ == '__main__':
    main()
