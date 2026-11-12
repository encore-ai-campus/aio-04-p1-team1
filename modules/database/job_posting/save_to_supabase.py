"""공고를 public.job_postings에 저장하고 컬럼·제약·저장 값을 검증."""
import argparse
import csv
import os
from dataclasses import fields
from datetime import date
from pathlib import Path
from uuid import UUID

from .schemas import JobPosting
from .wanted_crawler import _canonical_url

MODULE_DIR = Path(__file__).resolve().parent
COLUMNS = tuple(field.name for field in fields(JobPosting) if field.name != 'id')
EXPECTED_TYPES = {name: 'text' for name in COLUMNS}
EXPECTED_TYPES.update(id='uuid', min_experience_years='int4', max_experience_years='int4',
                      deadline_date='date', use_yn='bpchar')


def load_database_url():
    from dotenv import load_dotenv
    load_dotenv(MODULE_DIR.parents[2] / '.env', override=False)
    url = os.environ.get('DATABASE_URL', '').strip()
    if not url:
        raise ValueError('.env에 DATABASE_URL을 설정하세요.')
    return url


def validate_records(records):
    from .collect import RULES
    if not records:
        raise ValueError('저장할 공고가 없습니다.')
    seen = set()
    for row in records:
        if set(row) != set(COLUMNS) | {'id'}:
            raise ValueError('입력 컬럼이 새 테이블 설계와 다릅니다.')
        url = _canonical_url(row['source_url'])
        if url != row['source_url'] or url in seen:
            raise ValueError('정규화되지 않았거나 중복된 공고 URL입니다.')
        seen.add(url)
        if row['job_name'] not in RULES:
            raise ValueError('8개 직무에 없는 job_name입니다.')
        for name in ('title', 'company_name', 'region_name'):
            if not isinstance(row[name], str) or not row[name].strip():
                raise ValueError(f'{name} 필수값이 없습니다.')
        for name in ('min_experience_years', 'max_experience_years'):
            value = row[name]
            if value is not None and (type(value) is not int or value < 0):
                raise ValueError(f'{name}은 0 이상의 정수 또는 NULL이어야 합니다.')
        lower, upper = row['min_experience_years'], row['max_experience_years']
        if lower is not None and upper is not None and lower > upper:
            raise ValueError('최소 경력이 최대 경력보다 큽니다.')
        if row['deadline_date'] is not None:
            parsed = date.fromisoformat(row['deadline_date'])
            if parsed.isoformat() != row['deadline_date']:
                raise ValueError('마감 날짜는 YYYY-MM-DD 형식이어야 합니다.')
        if row['career_type'] == '신입' and upper is not None:
            raise ValueError('신입 공고의 최대 경력은 NULL이어야 합니다.')
        if row['use_yn'] not in ('Y', 'N'):
            raise ValueError('use_yn은 Y 또는 N이어야 합니다.')


def verify_schema(connection):
    columns = connection.execute("""SELECT column_name, udt_name, is_nullable, column_default
        FROM information_schema.columns WHERE table_schema='public' AND table_name='job_postings'""").fetchall()
    if {r['column_name']: r['udt_name'] for r in columns} != EXPECTED_TYPES:
        raise RuntimeError('기존 public.job_postings 컬럼이 사진의 설계와 다릅니다. 자동 변경하지 않습니다.')
    by_name = {r['column_name']: r for r in columns}
    for name in ('id', 'source_url', 'title', 'company_name', 'job_name', 'region_name', 'use_yn'):
        if by_name[name]['is_nullable'] != 'NO':
            raise RuntimeError(f'{name}의 NOT NULL 조건이 없습니다.')
    if 'gen_random_uuid()' not in (by_name['id']['column_default'] or ''):
        raise RuntimeError('id의 UUID 기본값이 다릅니다.')
    if "'Y'" not in (by_name['use_yn']['column_default'] or ''):
        raise RuntimeError('use_yn의 Y 기본값이 없습니다.')
    constraints = connection.execute("""SELECT contype, pg_get_constraintdef(oid) AS definition
        FROM pg_constraint WHERE conrelid='public.job_postings'::regclass""").fetchall()
    definitions = [r['definition'] for r in constraints]
    if not any(r['contype'] == 'p' and r['definition'] == 'PRIMARY KEY (id)' for r in constraints):
        raise RuntimeError('id 기본키가 다릅니다.')
    if not any(r['contype'] == 'u' and r['definition'] == 'UNIQUE (source_url)' for r in constraints):
        raise RuntimeError('source_url 고유 제약이 없습니다.')
    for name in ('min_experience_years', 'max_experience_years'):
        if not any(f'{name} >= 0' in definition for definition in definitions):
            raise RuntimeError(f'{name} 음수 방지 조건이 없습니다.')
    if not any('use_yn' in d and "'Y'" in d and "'N'" in d for d in definitions):
        raise RuntimeError('use_yn의 Y/N CHECK 조건이 없습니다.')


def save_records(records, database_url, *, replace=False):
    import psycopg
    from psycopg import sql
    from psycopg.rows import dict_row
    validate_records(records)
    updates = sql.SQL(', ').join(
        sql.SQL('{} = EXCLUDED.{}').format(sql.Identifier(name), sql.Identifier(name))
        for name in COLUMNS if name != 'source_url')
    statement = sql.SQL('INSERT INTO public.job_postings ({}) VALUES ({}) ON CONFLICT (source_url) DO UPDATE SET {}').format(
        sql.SQL(', ').join(map(sql.Identifier, COLUMNS)),
        sql.SQL(', ').join(sql.Placeholder() for _ in COLUMNS), updates)
    with psycopg.connect(database_url, sslmode='require', connect_timeout=15, row_factory=dict_row) as connection:
        connection.execute("SET LOCAL lock_timeout='5s'")
        connection.execute("SET LOCAL statement_timeout='30s'")
        connection.execute("SELECT pg_advisory_xact_lock(hashtextextended('career_compass_job_postings_collection',0))")
        exists = connection.execute("SELECT to_regclass('public.job_postings') IS NOT NULL AS yes").fetchone()['yes']
        if not exists:
            connection.execute((MODULE_DIR / 'job_postings.sql').read_text(encoding='utf-8'))
        verify_schema(connection)
        deleted = 0
        values = [tuple(row[name] for name in COLUMNS) for row in records]
        if replace:
            urls = [row['source_url'] for row in records]
            # 삭제 연쇄로 북마크 등을 잃지 않도록 참조 중인 데이터가 있으면 중단합니다.
            references = connection.execute("""SELECT f.conrelid::regclass::text AS child, a.attname AS column_name
                FROM pg_constraint f JOIN pg_attribute a ON a.attrelid=f.conrelid AND a.attnum=f.conkey[1]
                WHERE f.confrelid='public.job_postings'::regclass AND f.contype='f'""").fetchall()
            for ref in references:
                child = sql.Identifier(*ref['child'].split('.'))
                count = connection.execute(sql.SQL('SELECT count(*) AS n FROM {} c JOIN public.job_postings j ON c.{}=j.id WHERE j.source_url=ANY(%s)').format(child, sql.Identifier(ref['column_name'])), (urls,)).fetchone()['n']
                if count:
                    raise RuntimeError('기존 공고를 참조하는 데이터가 있어 삭제 후 교체를 중단합니다.')
            previous = connection.execute('DELETE FROM public.job_postings WHERE source_url=ANY(%s) RETURNING source_url,id', (urls,)).fetchall()
            deleted = len(previous)
            ids = {row['source_url']: row['id'] for row in previous}
            # 동일 공고의 내부 ID를 유지하면서 기존 행을 삭제 후 새 수집 값으로 삽입합니다.
            statement = sql.SQL('INSERT INTO public.job_postings (id,{}) VALUES (COALESCE(%s::uuid,gen_random_uuid()),{})').format(
                sql.SQL(', ').join(map(sql.Identifier, COLUMNS)),
                sql.SQL(', ').join(sql.Placeholder() for _ in COLUMNS))
            values = [(ids.get(row['source_url']),) + tuple(row[name] for name in COLUMNS) for row in records]
        with connection.cursor() as cursor:
            cursor.executemany(statement, values)
        saved = connection.execute('SELECT * FROM public.job_postings WHERE source_url=ANY(%s)',
                                   ([row['source_url'] for row in records],)).fetchall()
        by_url = {row['source_url']: row for row in saved}
        if len(saved) != len(records):
            raise RuntimeError('저장 건수가 일치하지 않아 롤백합니다.')
        for record in records:
            actual = by_url[record['source_url']]
            for name in COLUMNS:
                if name == 'deadline_date' and record[name] is not None:
                    equal = actual[name] == date.fromisoformat(record[name])
                else:
                    equal = actual[name] == record[name]
                if not equal:
                    raise RuntimeError(f'저장 후 {name} 값 검증에 실패해 롤백합니다.')
        counts = connection.execute('SELECT job_name,count(*) AS n FROM public.job_postings GROUP BY job_name ORDER BY job_name').fetchall()
        summary = {'table': 'public.job_postings', 'verified_rows': len(saved),
                   'counts_by_job': {r['job_name']: r['n'] for r in counts},
                   'dated_rows': sum(row['deadline_date'] is not None for row in saved),
                   'schema_verified': True, 'deleted_rows': deleted, 'replace': replace,
                   'newbie_max_nonnull': connection.execute("SELECT count(*) AS n FROM public.job_postings WHERE career_type='신입' AND max_experience_years IS NOT NULL").fetchone()['n']}
    # 위 트랜잭션을 커밋한 뒤 검증된 ID를 로컬 결과에 반영합니다.
    output = []
    for record in records:
        actual = by_url[record['source_url']]
        output.append({**record, 'id': str(actual['id']),
                       'deadline_date': actual['deadline_date'].isoformat() if actual['deadline_date'] else None})
    return output, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=MODULE_DIR / 'results/job_postings.csv')
    parser.add_argument('--replace', action='store_true', help='CSV에 있는 URL의 기존 행만 삭제 후 재삽입')
    args = parser.parse_args()
    try:
        with args.input.open(encoding='utf-8-sig', newline='') as stream:
            records = list(csv.DictReader(stream))
        for row in records:
            for name in ('min_experience_years','max_experience_years'):
                row[name] = int(row[name]) if row[name] else None
            for name in COLUMNS:
                if row[name] == '':
                    row[name] = None
            row['id'] = row['id'] or None
        saved, summary = save_records(records, load_database_url(), replace=args.replace)
        from .collect import write_records
        write_records(saved)
        print(summary)
    except Exception as exc:
        # 접속 문자열과 비밀번호가 포함될 수 있는 DB 예외 전문을 출력하지 않습니다.
        parser.exit(1, f'저장 실패: {type(exc).__name__} (SQLSTATE={getattr(exc, "sqlstate", None)})\n')

if __name__ == '__main__':
    main()
