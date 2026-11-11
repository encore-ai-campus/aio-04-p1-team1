"""회원별 자격증·교육 항목 SQL. 연결·인증은 호출 측 공통 의존성을 사용합니다."""
from fastapi import HTTPException
from psycopg import sql

TABLES = {
    'certificates': ('profiles_certifications', 'certification_name', 'certification_issuer', 'certification_acquired_date'),
    'courses': ('profiles_trainings', 'training_name', 'training_provider', 'training_completed_date'),
}


def projection(kind):
    _, name, organization, date = TABLES[kind]
    return sql.SQL("id, {} AS name, COALESCE({}, '') AS organization, {} AS completed_on").format(
        sql.Identifier(name), sql.Identifier(organization), sql.Identifier(date))


def list_entries(cursor, user_id, kind):
    table, name, _, _ = TABLES[kind]
    cursor.execute(sql.SQL("SELECT {} FROM public.{} WHERE user_id=%s AND use_yn='Y' ORDER BY {},id").format(
        projection(kind), sql.Identifier(table), sql.Identifier(name)), (user_id,))
    return cursor.fetchall()


def get_entry(cursor, user_id, kind, entry_id):
    table = TABLES[kind][0]
    cursor.execute(sql.SQL("SELECT {} FROM public.{} WHERE id=%s AND user_id=%s AND use_yn='Y'").format(
        projection(kind), sql.Identifier(table)), (entry_id, user_id))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(404, '항목을 찾을 수 없습니다.')
    return row


def create_entry(cursor, user_id, kind, body):
    table, name, organization, date = TABLES[kind]
    # 동시 추가에서도 회원별·종류별 기존 최대 50개 제한을 유지합니다.
    cursor.execute('SELECT pg_try_advisory_xact_lock(hashtextextended(%s, 91831)) AS acquired',
                   (str(user_id) + ':' + kind,))
    if not cursor.fetchone()['acquired']:
        raise HTTPException(409, '항목을 저장하고 있습니다. 잠시 후 다시 시도해 주세요.')
    cursor.execute(sql.SQL("SELECT count(*) AS n FROM public.{} WHERE user_id=%s AND use_yn='Y'").format(
        sql.Identifier(table)), (user_id,))
    if cursor.fetchone()['n'] >= 50:
        raise HTTPException(409, '종류별로 최대 50개까지 등록할 수 있습니다.')
    cursor.execute(sql.SQL('INSERT INTO public.{} (user_id,{},{},{}) VALUES (%s,%s,%s,%s) RETURNING {}').format(
        sql.Identifier(table), sql.Identifier(name), sql.Identifier(organization), sql.Identifier(date), projection(kind)),
        (user_id, body.name, body.organization, body.completed_on))
    return cursor.fetchone()


def update_entry(cursor, user_id, kind, entry_id, changes):
    table, name, organization, date = TABLES[kind]
    columns = {'name': name, 'organization': organization, 'completed_on': date}
    if not changes:
        raise HTTPException(422, '수정할 항목을 입력해 주세요.')
    assignments = sql.SQL(', ').join(sql.SQL('{}=%s').format(sql.Identifier(columns[key])) for key in changes)
    cursor.execute(sql.SQL("UPDATE public.{} SET {} WHERE id=%s AND user_id=%s AND use_yn='Y' RETURNING {}").format(
        sql.Identifier(table), assignments, projection(kind)), (*changes.values(), entry_id, user_id))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(404, '항목을 찾을 수 없습니다.')
    return row


def delete_entry(cursor, user_id, kind, entry_id):
    table = TABLES[kind][0]
    cursor.execute(sql.SQL("UPDATE public.{} SET use_yn='N' WHERE id=%s AND user_id=%s AND use_yn='Y' RETURNING id").format(
        sql.Identifier(table)), (entry_id, user_id))
    if not cursor.fetchone():
        raise HTTPException(404, '항목을 찾을 수 없습니다.')
