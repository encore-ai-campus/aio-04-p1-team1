"""플랫폼 설정 테이블 생성. profiles 테이블이 먼저 준비되어 있어야 합니다.

python -m modules.database.platform_settings.table --print-sql
python -m modules.database.platform_settings.table --dry-run
python -m modules.database.platform_settings.table
"""

import argparse
import json
from contextlib import closing
from pathlib import Path


MODULE_DIR = Path(__file__).resolve().parent
TABLE_COLUMNS = {
    'platform_settings': {
        'id': 'uuid',
        'user_id': 'uuid',
        'platform_name': 'text',
        'platform_email': 'text',
        'user_email': 'text',
        'use_yn': 'bpchar',
        'created_at': 'timestamptz',
    },
}


def schema_sql():
    """사용자가 직접 입력하는 수신 이메일을 포함한 생성 SQL."""
    return (MODULE_DIR / 'platform_settings.sql').read_text(encoding='utf-8')


def verify_schema(connection):
    rows = connection.execute(
        "SELECT column_name, udt_name, is_nullable FROM information_schema.columns "
        "WHERE table_schema='public' AND table_name='platform_settings'"
    ).fetchall()
    if {row['column_name']: row['udt_name'] for row in rows} != TABLE_COLUMNS['platform_settings']:
        raise RuntimeError('public.platform_settings의 컬럼·타입이 설계와 다릅니다.')
    if any(row['is_nullable'] != 'NO' for row in rows):
        raise RuntimeError('public.platform_settings의 필수 컬럼 조건이 다릅니다.')
    refs = connection.execute(
        "SELECT pg_get_constraintdef(oid) AS definition FROM pg_constraint "
        "WHERE conrelid='public.platform_settings'::regclass AND contype='f'"
    ).fetchall()
    if len(refs) != 1 or refs[0]['definition'] != (
        'FOREIGN KEY (user_id) REFERENCES profiles(user_id) ON DELETE CASCADE'
    ):
        raise RuntimeError('public.platform_settings의 외래키가 설계와 다릅니다.')


def create_tables(*, dry_run=False):
    from shared.database import get_db

    with closing(get_db()) as connections:
        connection = next(connections)
        with connection.transaction(force_rollback=dry_run):
            connection.execute("SET LOCAL lock_timeout='5s'")
            connection.execute("SET LOCAL statement_timeout='30s'")
            connection.execute(
                "SELECT pg_advisory_xact_lock(hashtextextended('career_compass_platform_settings_schema',0))"
            )
            connection.execute(schema_sql())
            verify_schema(connection)
            count = connection.execute(
                'SELECT count(*) AS n FROM public.platform_settings'
            ).fetchone()['n']
    return {'dry_run': dry_run, 'tables': {'platform_settings': count}}


def main():
    parser = argparse.ArgumentParser(description='플랫폼 설정 테이블 생성')
    parser.add_argument('--print-sql', action='store_true', help='생성·권한 SQL 출력')
    parser.add_argument('--dry-run', action='store_true', help='생성·검증 후 DB 변경 롤백')
    args = parser.parse_args()
    try:
        if args.print_sql:
            print(schema_sql())
            return
        print(json.dumps(create_tables(dry_run=args.dry_run), ensure_ascii=False, indent=2))
    except (ValueError, RuntimeError) as exc:
        parser.exit(1, f'생성 실패: {exc}\n')
    except Exception as exc:
        parser.exit(1, f'생성 실패: {type(exc).__name__} (SQLSTATE={getattr(exc, "sqlstate", None)})\n')


if __name__ == '__main__':
    main()
