"""최종 profiles 설계로 3개 테이블·권한·Auth 트리거·저장 RPC를 생성합니다.

python -m modules.database.profiles.table --dry-run
python -m modules.database.profiles.table
기존 public.users나 이전 프로필 구조를 읽거나 변경하지 않습니다.
"""
import argparse
import json
import os
import re
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parent
TABLE_COLUMNS = {
    'profiles': {'user_id': 'uuid', 'name': 'text', 'email': 'text', 'desired_jobs': '_text', 'skills': '_text', 'use_yn': 'bpchar'},
    'profiles_certifications': {'id': 'uuid', 'user_id': 'uuid', 'certification_name': 'text', 'certification_issuer': 'text', 'certification_acquired_date': 'date', 'use_yn': 'bpchar'},
    'profiles_trainings': {'id': 'uuid', 'user_id': 'uuid', 'training_name': 'text', 'training_provider': 'text', 'training_completed_date': 'date', 'use_yn': 'bpchar'},
}


def _table_name(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-z][a-z0-9_]*', value):
        raise ValueError('테이블·스키마 이름은 영문 소문자·숫자·밑줄만 사용하세요.')
    return value


def _layout(schema, table_names):
    schema = _table_name(schema)
    names = dict(table_names) if table_names is not None else {table: table for table in TABLE_COLUMNS}
    if set(names) != set(TABLE_COLUMNS) or len(set(names.values())) != 3:
        raise ValueError('서로 다른 프로필 테이블 이름 3개가 필요합니다.')
    return schema, {key: _table_name(value) for key, value in names.items()}


def schema_sql(*, schema='public', table_names=None):
    schema, names = _layout(schema, table_names)
    profile, cert, training = (names[key] for key in TABLE_COLUMNS)
    return f"""
CREATE TABLE IF NOT EXISTS {schema}.{profile} (
 user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
 name text NOT NULL, email text NOT NULL, desired_jobs text[], skills text[],
 use_yn char(1) NOT NULL DEFAULT 'Y' CHECK (use_yn IN ('Y','N'))
);
CREATE TABLE IF NOT EXISTS {schema}.{cert} (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 user_id uuid NOT NULL REFERENCES {schema}.{profile}(user_id) ON DELETE CASCADE,
 certification_name text NOT NULL CHECK (btrim(certification_name) <> ''),
 certification_issuer text, certification_acquired_date date,
 use_yn char(1) NOT NULL DEFAULT 'Y' CHECK (use_yn IN ('Y','N'))
);
CREATE TABLE IF NOT EXISTS {schema}.{training} (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 user_id uuid NOT NULL REFERENCES {schema}.{profile}(user_id) ON DELETE CASCADE,
 training_name text NOT NULL CHECK (btrim(training_name) <> ''),
 training_provider text, training_completed_date date,
 use_yn char(1) NOT NULL DEFAULT 'Y' CHECK (use_yn IN ('Y','N'))
);
CREATE INDEX IF NOT EXISTS {cert}_user_id_idx ON {schema}.{cert}(user_id);
CREATE INDEX IF NOT EXISTS {training}_user_id_idx ON {schema}.{training}(user_id);
"""


def access_sql(*, schema='public', table_names=None):
    schema, names = _layout(schema, table_names)
    statements = []
    for logical, table in names.items():
        qualified = f'{schema}.{table}'
        own = '(SELECT auth.uid())=user_id'
        active = f"EXISTS (SELECT 1 FROM {schema}.{names['profiles']} p WHERE p.user_id=(SELECT auth.uid()) AND p.use_yn='Y')"
        # 프로필 자체는 비활성 여부를 확인하기 위해 본인 조회를 허용합니다.
        # 비활성 계정의 수정 및 자격증·교육 CRUD는 RLS에서도 차단합니다.
        select_condition = own if logical == 'profiles' else f'{own} AND {active}'
        write_condition = f"{own} AND use_yn='Y'" if logical == 'profiles' else f'{own} AND {active}'
        statements.extend([
            f'ALTER TABLE {qualified} ENABLE ROW LEVEL SECURITY;',
            f'REVOKE ALL ON {qualified} FROM PUBLIC, anon, authenticated;',
            f'GRANT ALL ON {qualified} TO service_role;',
            f'GRANT SELECT ON {qualified} TO authenticated;',
        ])
        for action in ('select', 'insert', 'update', 'delete'):
            statements.append(f'DROP POLICY IF EXISTS career_compass_own_{action} ON {qualified};')
        statements.extend([
            f'CREATE POLICY career_compass_own_select ON {qualified} FOR SELECT TO authenticated USING ({select_condition});',
            f'CREATE POLICY career_compass_own_update ON {qualified} FOR UPDATE TO authenticated USING ({write_condition}) WITH CHECK ({own if logical == "profiles" else write_condition});',
        ])
        if logical == 'profiles':
            statements.extend([
                f'REVOKE UPDATE(user_id,name,email,desired_jobs,skills,use_yn) ON {qualified} FROM PUBLIC, anon, authenticated;',
                f'GRANT UPDATE(name,desired_jobs,skills,use_yn) ON {qualified} TO authenticated;',
            ])
        else:
            statements.extend([
                f'GRANT INSERT, UPDATE, DELETE ON {qualified} TO authenticated;',
                f'CREATE POLICY career_compass_own_insert ON {qualified} FOR INSERT TO authenticated WITH CHECK ({write_condition});',
                f'CREATE POLICY career_compass_own_delete ON {qualified} FOR DELETE TO authenticated USING ({write_condition});',
            ])
    return '\n'.join(statements)


def _exists(connection, name):
    return connection.execute('SELECT to_regclass(%s) IS NOT NULL AS yes', (name,)).fetchone()['yes']


def _rows(connection, table):
    from psycopg import sql
    if not _exists(connection, 'public.' + table):
        return []
    return connection.execute(sql.SQL('SELECT * FROM public.{}').format(sql.Identifier(table))).fetchall()


def _columns(connection, table):
    return {r['column_name']: r['udt_name'] for r in connection.execute(
        "SELECT column_name,udt_name FROM information_schema.columns WHERE table_schema='public' AND table_name=%s", (table,)).fetchall()}


def verify_schema(connection, *, schema='public', table_names=None):
    schema, names = _layout(schema, table_names)
    for logical, table in names.items():
        qualified = f'{schema}.{table}'
        rows = connection.execute("""SELECT column_name,udt_name,is_nullable,column_default,character_maximum_length
            FROM information_schema.columns WHERE table_schema=%s AND table_name=%s""", (schema,table)).fetchall()
        columns = {row['column_name']: row for row in rows}
        if {key: row['udt_name'] for key,row in columns.items()} != TABLE_COLUMNS[logical]:
            raise RuntimeError(f'{qualified}의 컬럼·타입이 최종 설계와 다릅니다.')
        required = {'user_id','name','email','use_yn'} if logical=='profiles' else {'id','user_id','use_yn', 'certification_name' if logical=='profiles_certifications' else 'training_name'}
        for key,row in columns.items():
            if (row['is_nullable']=='NO') != (key in required):
                raise RuntimeError(f'{qualified}.{key} NULL 조건이 다릅니다.')
        if columns['use_yn']['character_maximum_length'] != 1 or "'Y'" not in (columns['use_yn']['column_default'] or ''):
            raise RuntimeError(f'{qualified}.use_yn의 길이·기본값이 다릅니다.')
        if logical=='profiles':
            if any(columns[key]['column_default'] is not None for key in ('desired_jobs','skills')):
                raise RuntimeError('목록 컬럼에는 기본값이 없어야 합니다.')
        elif 'gen_random_uuid()' not in (columns['id']['column_default'] or ''):
            raise RuntimeError(f'{qualified}.id UUID 기본값이 다릅니다.')
        constraints = connection.execute("""SELECT contype,pg_get_constraintdef(oid) AS definition
            FROM pg_constraint WHERE conrelid=to_regclass(%s)""", (qualified,)).fetchall()
        pk = 'user_id' if logical=='profiles' else 'id'
        if not any(row['contype']=='p' and row['definition']==f'PRIMARY KEY ({pk})' for row in constraints):
            raise RuntimeError(f'{qualified} 기본키 검증 실패')
        checks = [row['definition'] for row in constraints if row['contype']=='c']
        if not any('use_yn' in value and "'Y'" in value and "'N'" in value for value in checks):
            raise RuntimeError(f'{qualified} Y/N 제약 검증 실패')
        if logical!='profiles':
            name = 'certification_name' if logical=='profiles_certifications' else 'training_name'
            if not any(f'btrim({name})' in value and "<> ''" in value for value in checks):
                raise RuntimeError(f'{qualified} 공백 이름 제약 검증 실패')
        target = 'auth.users' if logical=='profiles' else f"{schema}.{names['profiles']}"
        refs = connection.execute("""SELECT n.nspname||'.'||c.relname AS target,f.confdeltype,
                pg_get_constraintdef(f.oid) AS definition
            FROM pg_constraint f JOIN pg_class c ON c.oid=f.confrelid
            JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE f.conrelid=to_regclass(%s) AND f.contype='f'""", (qualified,)).fetchall()
        target_column = 'id' if logical=='profiles' else 'user_id'
        if len(refs)!=1 or refs[0]['target']!=target or refs[0]['confdeltype']!='c' or not refs[0]['definition'].startswith('FOREIGN KEY (user_id)') or f'({target_column})' not in refs[0]['definition']:
            raise RuntimeError(f'{qualified} 외래키 검증 실패')


def initialize_profiles(connection, *, dry_run=False):
    """호출자의 트랜잭션에서 최종 구조를 생성합니다. 기존 테이블은 자동 변경하지 않습니다."""
    from psycopg import sql
    connection.execute(schema_sql())
    verify_schema(connection)
    connection.execute(access_sql())
    connection.execute((MODULE_DIR/'profile_functions.sql').read_text(encoding='utf-8'))
    # Auth가 유일한 사용자 원본입니다. 기존 프로필 값은 덮어쓰지 않습니다.
    inserted = connection.execute("""INSERT INTO public.profiles(user_id,name,email)
        SELECT id,COALESCE(NULLIF(btrim(raw_user_meta_data->>'name'),''),
            NULLIF(btrim(raw_user_meta_data->>'full_name'),''),
            NULLIF(btrim(raw_user_meta_data->>'display_name'),''),''),email
        FROM auth.users WHERE email IS NOT NULL AND email<>''
        ON CONFLICT(user_id) DO NOTHING""").rowcount
    totals = {table: connection.execute(sql.SQL('SELECT count(*) AS n FROM public.{}').format(sql.Identifier(table))).fetchone()['n'] for table in TABLE_COLUMNS}
    return {'dry_run':dry_run,'tables':totals,'initialized_auth_profiles':inserted}


def create_tables(database_url, *, dry_run=False):
    import psycopg
    from psycopg.rows import dict_row
    from .profile_checks import verify_runtime
    with psycopg.connect(database_url, sslmode='require', connect_timeout=10, autocommit=True, row_factory=dict_row) as connection:
        with connection.transaction(force_rollback=dry_run):
            connection.execute("SET LOCAL lock_timeout='5s'")
            connection.execute("SET LOCAL statement_timeout='30s'")
            connection.execute("SELECT pg_advisory_xact_lock(hashtextextended('career_compass_profile_schema',0))")
            result = initialize_profiles(connection,dry_run=dry_run)
            result['checks'] = verify_runtime(connection)
    return result


def main():
    parser = argparse.ArgumentParser(description='최종 profiles 스키마 생성')
    parser.add_argument('--dry-run',action='store_true',help='생성·검증 후 DB 변경 롤백')
    parser.add_argument('--print-sql',action='store_true',help='생성·권한·함수 SQL 출력')
    args = parser.parse_args()
    try:
        if args.print_sql:
            print(schema_sql()+access_sql()+(MODULE_DIR/'profile_functions.sql').read_text())
            return
        from dotenv import load_dotenv
        load_dotenv(MODULE_DIR.parents[2]/'.env',override=False)
        url = os.environ.get('DATABASE_URL','').strip()
        if not url:
            raise ValueError('.env에 DATABASE_URL을 설정하세요.')
        print(json.dumps(create_tables(url,dry_run=args.dry_run),ensure_ascii=False,indent=2))
    except (ValueError,RuntimeError) as exc:
        parser.exit(1,f'생성 실패: {exc}\n')
    except Exception as exc:
        parser.exit(1,f'생성 실패: {type(exc).__name__} (SQLSTATE={getattr(exc,"sqlstate",None)})\n')

if __name__=='__main__':
    main()
