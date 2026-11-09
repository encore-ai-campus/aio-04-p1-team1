"""사용자/프로필/북마크 테이블 생성 및 Auth 사용자 정보 동기화.

프로젝트 루트에서 실행:
    python -m modules.database.table
    python -m modules.database.table --print-sql

공고 FK는 현재 데이터가 있는 *_mj 테이블을 기본으로 사용합니다.
정식 테이블로 연결하려면 --job-table job_postings --training-table training_postings.
동기화는 실행 시점의 auth.users 기준이며 같은 명령으로 재실행할 수 있습니다.
"""

import argparse
import json
import os
import re
from pathlib import Path


TABLE_COLUMNS = {
    'users': {'user_id': 'uuid', 'name': 'text', 'email': 'text', 'use_yn': 'bpchar'},
    'profiles': {
        'user_id': 'uuid', 'certification_name': 'text', 'certification_issuer': 'text',
        'certification_acquired_date': 'date', 'training_name': 'text',
        'training_provider': 'text', 'training_completed_date': 'date',
        'desired_job': 'text', 'skills': '_text', 'use_yn': 'bpchar',
    },
    'saved_jobs': {'user_id': 'uuid', 'job_id': 'uuid', 'created_at': 'timestamptz', 'use_yn': 'bpchar'},
    'saved_trainings': {'user_id': 'uuid', 'training_id': 'uuid', 'created_at': 'timestamptz', 'use_yn': 'bpchar'},
}


def _table_name(value):
    if not re.fullmatch(r'[a-z][a-z0-9_]*', value):
        raise ValueError('테이블명은 영문 소문자로 시작하고 소문자·숫자·밑줄만 사용할 수 있습니다.')
    return value


def schema_sql(job_table='job_posting_mj', training_table='training_posting_mj'):
    job_table, training_table = _table_name(job_table), _table_name(training_table)
    return f"""
CREATE TABLE IF NOT EXISTS public.users (
    user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    name text NOT NULL,
    email text NOT NULL,
    use_yn char(1) NOT NULL DEFAULT 'Y' CHECK (use_yn IN ('Y', 'N'))
);

CREATE TABLE IF NOT EXISTS public.profiles (
    user_id uuid PRIMARY KEY REFERENCES public.users(user_id) ON DELETE CASCADE,
    certification_name text,
    certification_issuer text,
    certification_acquired_date date,
    training_name text,
    training_provider text,
    training_completed_date date,
    desired_job text,
    skills text[] DEFAULT ARRAY[]::text[],
    use_yn char(1) NOT NULL DEFAULT 'Y' CHECK (use_yn IN ('Y', 'N'))
);

CREATE TABLE IF NOT EXISTS public.saved_jobs (
    user_id uuid REFERENCES public.profiles(user_id) ON DELETE CASCADE,
    job_id uuid REFERENCES public.{job_table}(id) ON DELETE CASCADE,
    created_at timestamptz DEFAULT now(),
    use_yn char(1) NOT NULL DEFAULT 'Y' CHECK (use_yn IN ('Y', 'N')),
    PRIMARY KEY (user_id, job_id)
);

CREATE TABLE IF NOT EXISTS public.saved_trainings (
    user_id uuid REFERENCES public.profiles(user_id) ON DELETE CASCADE,
    training_id uuid REFERENCES public.{training_table}(id) ON DELETE CASCADE,
    created_at timestamptz DEFAULT now(),
    use_yn char(1) NOT NULL DEFAULT 'Y' CHECK (use_yn IN ('Y', 'N')),
    PRIMARY KEY (user_id, training_id)
);
"""


SYNC_SQL = """
INSERT INTO public.users (user_id, name, email)
SELECT id,
       COALESCE(NULLIF(btrim(raw_user_meta_data->>'name'), ''),
                NULLIF(btrim(raw_user_meta_data->>'full_name'), ''),
                NULLIF(btrim(raw_user_meta_data->>'display_name'), ''), ''),
       email
FROM auth.users
WHERE email IS NOT NULL AND email <> ''
ON CONFLICT (user_id) DO UPDATE SET name = EXCLUDED.name, email = EXCLUDED.email;

INSERT INTO public.profiles (user_id)
SELECT user_id FROM public.users
ON CONFLICT (user_id) DO NOTHING;
"""


def access_sql():
    """로그인한 사용자가 자신의 데이터만 접근하도록 설정합니다."""
    statements = []
    for table in TABLE_COLUMNS:
        statements.extend([
            f'ALTER TABLE public.{table} ENABLE ROW LEVEL SECURITY;',
            f'REVOKE ALL ON public.{table} FROM PUBLIC, anon, authenticated;',
            f'GRANT ALL ON public.{table} TO service_role;',
            f'DROP POLICY IF EXISTS career_compass_own_select ON public.{table};',
            f'''CREATE POLICY career_compass_own_select ON public.{table}
                FOR SELECT TO authenticated USING ((SELECT auth.uid()) = user_id);''',
            f'GRANT SELECT ON public.{table} TO authenticated;',
            f'DROP POLICY IF EXISTS career_compass_own_update ON public.{table};',
            f'''CREATE POLICY career_compass_own_update ON public.{table}
                FOR UPDATE TO authenticated USING ((SELECT auth.uid()) = user_id)
                WITH CHECK ((SELECT auth.uid()) = user_id);''',
        ])
        if table == 'users':
            # 이메일은 Auth에서 동기화합니다. API를 통한 직접 변경 권한은 주지 않습니다.
            statements.append('GRANT UPDATE (name, use_yn) ON public.users TO authenticated;')
        else:
            statements.extend([
                f'GRANT INSERT, UPDATE, DELETE ON public.{table} TO authenticated;',
                f'DROP POLICY IF EXISTS career_compass_own_insert ON public.{table};',
                f'''CREATE POLICY career_compass_own_insert ON public.{table}
                    FOR INSERT TO authenticated WITH CHECK ((SELECT auth.uid()) = user_id);''',
                f'DROP POLICY IF EXISTS career_compass_own_delete ON public.{table};',
                f'''CREATE POLICY career_compass_own_delete ON public.{table}
                    FOR DELETE TO authenticated USING ((SELECT auth.uid()) = user_id);''',
            ])
    return '\n'.join(statements)


def verify_schema(connection, job_table, training_table):
    for table, expected in TABLE_COLUMNS.items():
        rows = connection.execute(
            "SELECT column_name, udt_name FROM information_schema.columns WHERE table_schema='public' AND table_name=%s",
            (table,),
        ).fetchall()
        if dict(rows) != expected:
            raise RuntimeError(f'public.{table}의 컬럼이 요청한 구조와 다릅니다. 기존 데이터를 변경하지 않고 롤백합니다.')
    expected_fks = {
        'users': {'auth.users'}, 'profiles': {'public.users'},
        'saved_jobs': {'public.profiles', f'public.{job_table}'},
        'saved_trainings': {'public.profiles', f'public.{training_table}'},
    }
    for table, expected in expected_fks.items():
        rows = connection.execute("""
            SELECT n.nspname || '.' || c.relname, fk.confdeltype
            FROM pg_constraint fk JOIN pg_class c ON c.oid=fk.confrelid
            JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE fk.conrelid=to_regclass(%s) AND fk.contype='f'
        """, (f'public.{table}',)).fetchall()
        if {row[0] for row in rows} != expected or any(row[1] != 'c' for row in rows):
            raise RuntimeError(f'public.{table}의 외래키/삭제 연쇄 설정이 요청과 다릅니다.')


def create_tables(database_url, job_table='job_posting_mj', training_table='training_posting_mj'):
    import psycopg
    job_table, training_table = _table_name(job_table), _table_name(training_table)
    with psycopg.connect(database_url, sslmode='require', connect_timeout=10) as connection:
        connection.execute("SET LOCAL lock_timeout = '5s'")
        connection.execute("SET LOCAL statement_timeout = '30s'")
        for table in (job_table, training_table):
            exists = connection.execute('SELECT to_regclass(%s) IS NOT NULL', (f'public.{table}',)).fetchone()[0]
            if not exists:
                raise ValueError(f'북마크 연결 대상 public.{table}이 없습니다. 공고 테이블을 먼저 준비하세요.')
        connection.execute(schema_sql(job_table, training_table))
        verify_schema(connection, job_table, training_table)
        connection.execute(SYNC_SQL)
        connection.execute(access_sql())
        totals = {table: connection.execute(f'SELECT count(*) FROM public.{table}').fetchone()[0] for table in TABLE_COLUMNS}
        source = connection.execute("""
            SELECT count(*), count(*) FILTER (WHERE email IS NULL OR email=''),
                   count(*) FILTER (WHERE COALESCE(NULLIF(btrim(raw_user_meta_data->>'name'), ''),
                       NULLIF(btrim(raw_user_meta_data->>'full_name'), ''),
                       NULLIF(btrim(raw_user_meta_data->>'display_name'), '')) IS NULL)
            FROM auth.users
        """).fetchone()
        missing = connection.execute("""
            SELECT count(*) FROM auth.users a LEFT JOIN public.users u ON u.user_id=a.id
            WHERE a.email IS NOT NULL AND a.email<>'' AND (u.user_id IS NULL OR u.email IS DISTINCT FROM a.email)
        """).fetchone()[0]
        if missing:
            raise RuntimeError('Auth 사용자 동기화 검증에 실패해 롤백합니다.')
    return {'tables': totals, 'auth_users': source[0], 'skipped_no_email': source[1],
            'missing_name_metadata': source[2], 'skills_type': 'text[]',
            'job_reference': f'public.{job_table}.id', 'training_reference': f'public.{training_table}.id'}


def main():
    parser = argparse.ArgumentParser(description='사용자·프로필·북마크 테이블 생성 및 Auth 데이터 반영')
    parser.add_argument('--job-table', default='job_posting_mj')
    parser.add_argument('--training-table', default='training_posting_mj')
    parser.add_argument('--print-sql', action='store_true', help='DB 접속 없이 SQL 확인')
    args = parser.parse_args()
    try:
        if args.print_sql:
            print(schema_sql(args.job_table, args.training_table) + SYNC_SQL + access_sql())
            return
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parents[2] / '.env', override=False)
        database_url = os.environ.get('DATABASE_URL', '').strip()
        if not database_url:
            raise ValueError('.env에 DATABASE_URL을 설정하세요.')
        result = create_tables(database_url, args.job_table, args.training_table)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, RuntimeError) as exc:
        parser.exit(1, f'생성 실패: {exc}\n')
    except Exception as exc:
        # 비밀번호나 사용자 개인정보가 포함될 수 있어 예외 전문은 출력하지 않습니다.
        parser.exit(1, f'생성 실패: {type(exc).__name__} (SQLSTATE={getattr(exc, "sqlstate", None)})\n')


if __name__ == '__main__':
    main()
