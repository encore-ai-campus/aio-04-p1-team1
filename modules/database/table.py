"""전체 스키마 실행 연결 및 북마크 테이블 생성.

프로필 3개 테이블의 실제 생성 코드는 profiles/table.py에 있습니다.
python -m modules.database.table --dry-run
"""
import argparse
import json
import os
from pathlib import Path

from modules.database.profiles import table as profiles
from modules.database.profiles.table import _table_name, _exists, _rows, _columns
from modules.database.profiles.profile_checks import verify_runtime

MODULE_DIR = Path(__file__).resolve().parent
TABLE_COLUMNS = {
    **profiles.TABLE_COLUMNS,
    'saved_jobs': {'user_id': 'uuid', 'job_id': 'uuid', 'created_at': 'timestamptz', 'use_yn': 'bpchar'},
    'saved_trainings': {'user_id': 'uuid', 'training_id': 'uuid', 'created_at': 'timestamptz', 'use_yn': 'bpchar'},
}


def bookmark_schema_sql(job_table='job_posting_mj', training_table='training_posting'):
    job_table, training_table = _table_name(job_table), _table_name(training_table)
    return f"""
CREATE TABLE IF NOT EXISTS public.saved_jobs (
 user_id uuid REFERENCES public.profiles(user_id) ON DELETE CASCADE,
 job_id uuid REFERENCES public.{job_table}(id) ON DELETE CASCADE,
 created_at timestamptz DEFAULT now(),
 use_yn char(1) NOT NULL DEFAULT 'Y' CHECK (use_yn IN ('Y','N')),
 PRIMARY KEY (user_id,job_id)
);
CREATE TABLE IF NOT EXISTS public.saved_trainings (
 user_id uuid REFERENCES public.profiles(user_id) ON DELETE CASCADE,
 training_id uuid REFERENCES public.{training_table}(id) ON DELETE CASCADE,
 created_at timestamptz DEFAULT now(),
 use_yn char(1) NOT NULL DEFAULT 'Y' CHECK (use_yn IN ('Y','N')),
 PRIMARY KEY (user_id,training_id)
);
"""


def schema_sql(job_table='job_posting_mj', training_table='training_posting'):
    return profiles.schema_sql() + bookmark_schema_sql(job_table, training_table)


def bookmark_access_sql():
    statements = []
    for table in ('saved_jobs', 'saved_trainings'):
        statements.extend([
            f'ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY;',
            f'REVOKE ALL ON public.{table} FROM PUBLIC, anon, authenticated;',
            f'GRANT ALL ON public.{table} TO service_role;',
            f'GRANT SELECT, INSERT, UPDATE, DELETE ON public.{table} TO authenticated;',
        ])
        for action in ('select', 'insert', 'update', 'delete'):
            statements.append(f'DROP POLICY IF EXISTS career_compass_own_{action} ON public.{table};')
            clause = ('WITH CHECK' if action == 'insert' else 'USING') + ' ((SELECT auth.uid())=user_id)'
            if action == 'update':
                clause += ' WITH CHECK ((SELECT auth.uid())=user_id)'
            statements.append(f'CREATE POLICY career_compass_own_{action} ON public.{table} FOR {action.upper()} TO authenticated {clause};')
    return '\n'.join(statements)


def access_sql():
    return profiles.access_sql() + '\n' + bookmark_access_sql()


def _resolve_post_table(connection, explicit, saved_table, candidates):
    if explicit:
        table = _table_name(explicit)
    else:
        result = connection.execute("""
            SELECT c.relname FROM pg_constraint f JOIN pg_class c ON c.oid=f.confrelid
            JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE f.conrelid=to_regclass(%s) AND f.contype='f'
              AND n.nspname='public' AND c.relname<>'profiles'
        """, ('public.' + saved_table,)).fetchall()
        table = result[0]['relname'] if len(result) == 1 else next((name for name in candidates if _exists(connection, 'public.' + name)), None)
    if not table or not _exists(connection, 'public.' + table):
        raise ValueError('북마크가 참조할 공고 테이블이 없습니다.')
    return _table_name(table)


def verify_schema(connection, job_table, training_table):
    profiles.verify_schema(connection)
    for table in ('saved_jobs', 'saved_trainings'):
        expected = TABLE_COLUMNS[table]
        if _columns(connection, table) != expected:
            raise RuntimeError(f'public.{table}의 컬럼이 새 설계와 다릅니다.')
    expected = {'saved_jobs': {'public.profiles', 'public.'+job_table},
                'saved_trainings': {'public.profiles', 'public.'+training_table}}
    for table, targets in expected.items():
        refs = connection.execute("""
            SELECT n.nspname||'.'||c.relname AS target,f.confdeltype
            FROM pg_constraint f JOIN pg_class c ON c.oid=f.confrelid
            JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE f.conrelid=to_regclass(%s) AND f.contype='f'
        """, ('public.'+table,)).fetchall()
        if {r['target'] for r in refs} != targets or any(r['confdeltype']!='c' for r in refs):
            raise RuntimeError(f'public.{table} 외래키 검증에 실패했습니다.')


def create_tables(database_url, job_table=None, training_table=None, *, dry_run=False):
    import psycopg
    from psycopg import sql
    from psycopg.rows import dict_row
    with psycopg.connect(database_url, sslmode='require', connect_timeout=10, autocommit=True, row_factory=dict_row) as connection:
        with connection.transaction(force_rollback=dry_run):
            connection.execute("SET LOCAL lock_timeout='5s'")
            connection.execute("SET LOCAL statement_timeout='30s'")
            connection.execute("SELECT pg_advisory_xact_lock(hashtextextended('career_compass_profile_schema',0))")
            job_table = _resolve_post_table(connection, job_table, 'saved_jobs', ('job_posting','job_posting_mj','job_postings'))
            training_table = _resolve_post_table(connection, training_table, 'saved_trainings', ('training_posting','training_posting_mj','training_postings'))
            snapshot = {}
            for table in ('saved_jobs', 'saved_trainings'):
                if _exists(connection, 'public.' + table):
                    connection.execute(sql.SQL('LOCK TABLE public.{} IN SHARE ROW EXCLUSIVE MODE').format(sql.Identifier(table)))
                snapshot[table] = _rows(connection, table)
            result = profiles.initialize_profiles(connection, dry_run=dry_run)
            connection.execute(bookmark_schema_sql(job_table, training_table))
            connection.execute(bookmark_access_sql())
            verify_schema(connection, job_table, training_table)
            result['checks'] = verify_runtime(connection)
            for table, before_rows in snapshot.items():
                before = {json.dumps(row, sort_keys=True, default=str) for row in before_rows}
                after = {json.dumps(row, sort_keys=True, default=str) for row in _rows(connection, table)}
                if before != after:
                    raise RuntimeError('기존 북마크 데이터가 변경되어 전체 롤백합니다.')
                result['tables'][table] = len(_rows(connection, table))
            result.update(job_reference='public.'+job_table+'.id', training_reference='public.'+training_table+'.id')
    return result


def main():
    parser = argparse.ArgumentParser(description='최종 프로필·북마크 스키마 생성')
    parser.add_argument('--job-table')
    parser.add_argument('--training-table')
    parser.add_argument('--dry-run',action='store_true',help='전체 생성을 검증한 뒤 DB 변경 롤백')
    parser.add_argument('--print-sql',action='store_true',help='새 스키마/권한/함수 SQL 확인 (Auth 초기 반영은 Python 실행 필요)')
    args=parser.parse_args()
    try:
        if args.print_sql:
            print(schema_sql(args.job_table or 'job_posting_mj',args.training_table or 'training_posting')+access_sql()+(profiles.MODULE_DIR/'profile_functions.sql').read_text())
            return
        from dotenv import load_dotenv
        load_dotenv(MODULE_DIR.parents[1]/'.env',override=False)
        url=os.environ.get('DATABASE_URL','').strip()
        if not url:raise ValueError('.env에 DATABASE_URL을 설정하세요.')
        print(json.dumps(create_tables(url,args.job_table,args.training_table,dry_run=args.dry_run),ensure_ascii=False,indent=2))
    except (ValueError,RuntimeError) as exc:
        parser.exit(1,f'생성 실패: {exc}\n')
    except Exception as exc:
        parser.exit(1,f'생성 실패: {type(exc).__name__} (SQLSTATE={getattr(exc,"sqlstate",None)})\n')


if __name__=='__main__':
    main()
