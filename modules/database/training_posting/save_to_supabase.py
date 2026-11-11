"""훈련과정 JSON을 요청한 9개 컬럼의 public.training_posting에 저장합니다."""

import argparse
import json
import os
from dataclasses import fields
from datetime import date
from pathlib import Path
from uuid import UUID

from modules.database.training_posting.schemas import TrainingPosting


MODULE_DIR = Path(__file__).resolve().parent
COLUMNS = tuple(field.name for field in fields(TrainingPosting))


def validate_records(records):
    if not isinstance(records, list):
        raise ValueError("훈련과정 JSON 배열이 필요합니다.")
    urls, ids = set(), set()
    for row in records:
        if set(row) != set(COLUMNS):
            raise ValueError("훈련과정 컬럼이 요청한 모델과 다릅니다.")
        for name in ("work24_training_id", "source_url", "title"):
            if not isinstance(row[name], str) or not row[name].strip():
                raise ValueError(f"{name} 값이 필요합니다.")
        if row['use_yn'] not in ('Y', 'N'):
            raise ValueError("use_yn은 Y 또는 N이어야 합니다.")
        for name in ('training_start_dt', 'training_end_dt'):
            if row[name] is not None and date.fromisoformat(row[name]).isoformat() != row[name]:
                raise ValueError("날짜는 YYYY-MM-DD 형식이어야 합니다.")
        if row['training_start_dt'] and row['training_end_dt'] and row['training_start_dt'] > row['training_end_dt']:
            raise ValueError("교육 종료일이 시작일보다 빠릅니다.")
        if row['id'] is not None:
            UUID(row['id'])
        if row['source_url'] in urls or row['work24_training_id'] in ids:
            raise ValueError("원본 링크 또는 훈련과정 ID가 중복되었습니다.")
        urls.add(row['source_url'])
        ids.add(row['work24_training_id'])


def save_records(records, database_url):
    import psycopg
    from psycopg import sql
    from psycopg.rows import dict_row

    validate_records(records)
    insert_columns = [name for name in COLUMNS if name != 'id']
    statement = sql.SQL('INSERT INTO public.training_posting ({}) VALUES ({}) ON CONFLICT (source_url) DO UPDATE SET {}').format(
        sql.SQL(', ').join(map(sql.Identifier, insert_columns)),
        sql.SQL(', ').join(sql.Placeholder() for _ in insert_columns),
        sql.SQL(', ').join(sql.SQL('{} = EXCLUDED.{}').format(sql.Identifier(name), sql.Identifier(name))
                          for name in insert_columns if name not in ('source_url', 'use_yn')),
    )
    with psycopg.connect(database_url, sslmode='require', connect_timeout=10, row_factory=dict_row) as connection:
        connection.execute("SET LOCAL statement_timeout = '30s'")
        connection.execute((MODULE_DIR / 'training_posting.sql').read_text())
        schema = connection.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='public' AND table_name='training_posting'").fetchall()
        actual_types = {row['column_name']: row['data_type'] for row in schema}
        expected_types = {name: ('uuid' if name == 'id' else 'date' if name.endswith('_dt') else 'character' if name == 'use_yn' else 'text') for name in COLUMNS}
        if actual_types != expected_types:
            raise RuntimeError('기존 테이블 구조가 요청한 9개 컬럼과 달라 롤백합니다.')
        with connection.cursor() as cursor:
            cursor.executemany(statement, [tuple(row[name] for name in insert_columns) for row in records])
        saved = connection.execute('SELECT * FROM public.training_posting WHERE source_url = ANY(%s)',
                                   ([row['source_url'] for row in records],)).fetchall() if records else []
        saved = [{k: str(v) if isinstance(v, (date, UUID)) else v for k, v in row.items()} for row in saved]
        by_url = {row['source_url']: row for row in saved}
        if len(by_url) != len(records):
            raise RuntimeError('저장 후 건수 불일치로 롤백합니다.')
        for record in records:
            if any(by_url[record['source_url']][name] != record[name] for name in COLUMNS if name not in ('id', 'use_yn')):
                raise RuntimeError('저장 후 데이터 비교 실패로 롤백합니다.')
        count = connection.execute('SELECT count(*) AS count FROM public.training_posting').fetchone()['count']
    return [by_url[row['source_url']] for row in records], {'table': 'public.training_posting', 'verified_rows': len(saved), 'table_total_rows': count}


def load_database_url():
    from dotenv import load_dotenv
    load_dotenv(MODULE_DIR.parents[2] / '.env', override=False)
    value = os.environ.get('DATABASE_URL', '').strip()
    if not value:
        raise ValueError('.env에 DATABASE_URL을 설정하세요.')
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=MODULE_DIR / 'results/training_postings.json')
    parser.add_argument('--create-only', action='store_true')
    args = parser.parse_args()
    try:
        records = [] if args.create_only else json.loads(args.input.read_text())
        saved, summary = save_records(records, load_database_url())
        if not args.create_only:
            args.input.write_text(json.dumps(saved, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(summary, ensure_ascii=False))
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(1, f'저장 실패: {exc}\n')
    except Exception as exc:
        parser.exit(1, f'저장 실패: {type(exc).__name__} (SQLSTATE={getattr(exc, "sqlstate", None)})\n')


if __name__ == '__main__':
    main()
