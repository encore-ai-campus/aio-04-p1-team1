"""saved_jobs / saved_trainings를 기존 관심목록 응답 형태로 연결합니다."""
from contextlib import contextmanager
from datetime import datetime, time, timezone, timedelta
import json
from uuid import UUID

from fastapi import HTTPException
from psycopg import Error, sql
from psycopg.errors import ForeignKeyViolation

TABLES = {
    'job': ('saved_jobs', 'job_id', 'job_posting_mj'),
    'course': ('saved_trainings', 'training_id', 'training_posting'),
}


def not_found():
    raise HTTPException(404, detail={'code':'BOOKMARK_NOT_FOUND','message':'저장한 정보를 찾을 수 없습니다.'})


@contextmanager
def database_operation(db):
    """공통 연결을 사용하고 오류 응답에 SQL·연결 정보를 노출하지 않습니다."""
    try:
        with db.transaction():
            yield
    except ForeignKeyViolation:
        raise HTTPException(409, '회원 기본 프로필 또는 원본 공고가 없습니다. 연결 상태를 확인해 주세요.') from None
    except Error:
        raise HTTPException(503, '관심목록을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.') from None


def member_scope(cursor, user_id):
    cursor.execute('SET LOCAL ROLE authenticated')
    cursor.execute("SELECT set_config('request.jwt.claims', %s, true), set_config('request.jwt.claim.sub', %s, true)",
                   (json.dumps({'sub':str(user_id),'role':'authenticated'}),str(user_id)))


def decode_id(value):
    try:
        kind, identifier = value.split(':', 1)
        if kind not in TABLES:
            raise ValueError()
        return kind, UUID(identifier)
    except (ValueError, AttributeError):
        raise HTTPException(422, '저장 정보 ID는 job:UUID 또는 course:UUID 형식이어야 합니다.') from None


def own_saved(cursor, user_id):
    """저장 행은 RLS 아래에서 본인 것만 읽습니다."""
    member_scope(cursor, user_id)
    cursor.execute('''SELECT 'job' AS item_type, job_id AS source_id, created_at
                      FROM public.saved_jobs WHERE user_id=%s AND use_yn='Y'
                      UNION ALL
                      SELECT 'course', training_id, created_at
                      FROM public.saved_trainings WHERE user_id=%s AND use_yn='Y' ''',
                   (user_id,user_id))
    rows=cursor.fetchall()
    # 원본 공고에는 현재 authenticated 조회 정책이 없습니다.
    # 원본 조회만 공통 서버 연결 권한으로 처리하고, RLS로 얻은 본인 ID 목록으로 제한합니다.
    cursor.execute('RESET ROLE')
    return rows


def originals(cursor, kind, identifiers):
    if not identifiers:
        return {}
    table=TABLES[kind][2]
    cursor.execute(sql.SQL('SELECT * FROM public.{} WHERE id=ANY(%s)').format(sql.Identifier(table)),
                   (list(identifiers),))
    return {row['id']:row for row in cursor.fetchall()}


def item(saved, original, user_id):
    kind=saved['item_type']
    deadline=None
    if kind=='job' and original.get('deadline_date'):
        deadline=datetime.combine(original['deadline_date'],time(23,59,59),tzinfo=timezone(timedelta(hours=9)))
    return {
        'id':kind+':'+str(saved['source_id']),
        'user_id':str(user_id), 'item_type':kind,
        'source':TABLES[kind][2], 'source_id':str(saved['source_id']),
        'title':original['title'],
        'organization':original['company_name'] if kind=='job' else (original.get('center_name') or '교육기관 확인 필요'),
        'original_url':original['source_url'],
        'location':original.get('address') if kind=='job' else original.get('center_address'),
        'deadline':deadline,
        # 교육 종료일은 모집 마감일이 아니므로 deadline으로 사용하지 않습니다.
        'cost':None, 'is_online':None,
        'created_at':saved['created_at'],
    }


def list_items(db, user_id, kind=None, query=None, page=1, size=20):
    with database_operation(db), db.cursor() as cursor:
        saved=own_saved(cursor,user_id)
        data={key:originals(cursor,key,[r['source_id'] for r in saved if r['item_type']==key]) for key in TABLES}
        items=[item(r,data[r['item_type']][r['source_id']],user_id) for r in saved if r['source_id'] in data[r['item_type']]]
    # 검색 조건과 무관한 탭별 개수와 안정적인 표시 순서를 유지합니다.
    items.sort(key=lambda row: (row['created_at'] or datetime.min.replace(tzinfo=timezone.utc),row['id']),reverse=True)
    counts={'all':len(items),'job':sum(row['item_type']=='job' for row in items),'course':sum(row['item_type']=='course' for row in items)}
    needle=(query or '').strip().casefold()
    selected=[row for row in items if (not kind or row['item_type']==kind) and
              (not needle or needle in (row['title']+' '+row['organization']).casefold())]
    return {'items':selected[(page-1)*size:page*size],'total':len(selected),'counts':counts,'page':page,'size':size}


def resolve_original(cursor, kind, source_id, original_url=None):
    table=TABLES[kind][2]
    try:
        identifier=UUID(source_id)
    except ValueError:
        identifier=None
    if identifier is not None:
        rows=originals(cursor,kind,[identifier])
        if identifier in rows:
            return rows[identifier]
    else:
        # 기존 요청이 원문 URL 또는 교육 외부 ID를 보내는 경우에도 연결합니다.
        conditions=[];params=[]
        if kind=='course':
            conditions.append(sql.SQL('work24_training_id=%s'));params.append(source_id)
        if original_url:
            conditions.append(sql.SQL('source_url=%s'));params.append(str(original_url))
        if conditions:
            cursor.execute(sql.SQL('SELECT * FROM public.{} WHERE {} LIMIT 2').format(
                sql.Identifier(table),sql.SQL(' OR ').join(conditions)),params)
            rows=cursor.fetchall()
            if len(rows)==1:
                return rows[0]
            if len(rows)>1:
                raise HTTPException(409, '원본 공고를 하나로 식별할 수 없습니다. source_id에 원본 공고 UUID를 보내 주세요.')
    raise HTTPException(404, '원본 공고가 없습니다. 저장할 공고의 UUID를 확인해 주세요.')


def create_item(db, user_id, body):
    kind=body.item_type.value
    saved_table,id_column,_=TABLES[kind]
    with database_operation(db), db.cursor() as cursor:
        original=resolve_original(cursor,kind,body.source_id,body.original_url)
        cursor.execute('SELECT 1 FROM public.profiles WHERE user_id=%s',(user_id,))
        if not cursor.fetchone():
            raise HTTPException(409, '회원 기본 프로필이 없어 저장할 수 없습니다. 회원정보 연결을 먼저 확인해 주세요.')
        member_scope(cursor,user_id)
        cursor.execute(sql.SQL('''INSERT INTO public.{table} (user_id,{column},use_yn)
            VALUES (%s,%s,'Y') ON CONFLICT (user_id,{column}) DO UPDATE
            SET use_yn='Y',created_at=now() WHERE {table}.use_yn='N'
            RETURNING {column} AS source_id,created_at''').format(
                table=sql.Identifier(saved_table),column=sql.Identifier(id_column)),(user_id,original['id']))
        saved=cursor.fetchone()
        if not saved:
            raise HTTPException(409,detail={'code':'BOOKMARK_ALREADY_EXISTS','message':'이미 저장한 정보입니다.'})
        saved['item_type']=kind
        cursor.execute('RESET ROLE')
        return item(saved,original,user_id)


def read_item(db, user_id, bookmark_id):
    kind,identifier=decode_id(bookmark_id)
    # 목록의 페이지 크기에 의존하지 않고 본인 행 하나를 정확히 조회합니다.
    table,column,_=TABLES[kind]
    with database_operation(db), db.cursor() as cursor:
        member_scope(cursor,user_id)
        cursor.execute(sql.SQL('SELECT {} AS source_id,created_at FROM public.{} WHERE user_id=%s AND {}=%s AND use_yn=\'Y\'').format(
            sql.Identifier(column),sql.Identifier(table),sql.Identifier(column)),(user_id,identifier))
        saved=cursor.fetchone()
        cursor.execute('RESET ROLE')
        if not saved:
            not_found()
        source=originals(cursor,kind,[identifier]).get(identifier)
        if not source:
            not_found()
        saved['item_type']=kind
        return item(saved,source,user_id)


def delete_item(db, user_id, bookmark_id):
    kind,identifier=decode_id(bookmark_id)
    table,column,_=TABLES[kind]
    with database_operation(db), db.cursor() as cursor:
        member_scope(cursor,user_id)
        cursor.execute(sql.SQL('UPDATE public.{} SET use_yn=\'N\' WHERE user_id=%s AND {}=%s AND use_yn=\'Y\' RETURNING {}').format(
            sql.Identifier(table),sql.Identifier(column),sql.Identifier(column)),(user_id,identifier))
        if not cursor.fetchone():
            not_found()
        cursor.execute('RESET ROLE')
