"""public.training_posts_sms access. Course data is read from DB, never from the browser."""
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
import json
import logging
from psycopg.rows import tuple_row

from shared.database import get_db

LOGGER = logging.getLogger('uvicorn.error')
KST = timezone(timedelta(hours=9))


class CatalogueStorageError(Exception):
    """Safe message, without connection strings or credentials."""


@contextmanager
def database():
    try:
        # Reuse the shared session's commit, rollback and connection cleanup.
        with contextmanager(get_db)() as connection:
            # Existing catalogue and job readers consume positional rows.
            with connection.cursor(row_factory=tuple_row) as cursor:
                cursor.execute("SET LOCAL statement_timeout = '30s'")
                yield cursor
    except CatalogueStorageError:
        raise
    except Exception as exc:
        LOGGER.warning('Training catalogue database operation failed (%s)', type(exc).__name__)
        raise CatalogueStorageError('교육 저장소에 연결하지 못했습니다. 잠시 후 다시 확인해 주세요.') from None


def read_catalogue(start, end):
    # Import lazily to avoid a repository/service import cycle.
    from modules.training_posts.service import CATEGORIES, normalize_course
    with database() as cursor:
        cursor.execute('''SELECT category_code, raw_payload, last_seen_at
                          FROM public.training_posts_sms
                          WHERE start_date BETWEEN %s AND %s
                          ORDER BY start_date DESC, category_code, external_course_id, course_round''', (start, end))
        rows = cursor.fetchall()
        cursor.execute('SELECT max(last_seen_at) FROM public.training_posts_sms')
        saved_at = cursor.fetchone()[0]
    courses = []
    for code, raw, _seen_at in rows:
        if code not in CATEGORIES:
            continue
        if isinstance(raw, str):
            raw = json.loads(raw)
        if isinstance(raw, dict):
            courses.append(normalize_course(raw, code))
    return {
        'courses': courses,
        'categories': [{'code': code, 'name': name} for code, name in CATEGORIES.items()],
        'errors': [], 'source': 'supabase',
        'fetchedAt': saved_at.astimezone(KST).strftime('%Y-%m-%d %H:%M:%S') if saved_at else '저장 자료 없음',
        'start': start.isoformat(), 'end': end.isoformat(),
    }


def replace_snapshot(groups):
    """Explicit one-time import only; an incomplete API response never replaces existing data."""
    from modules.training_posts.service import CATEGORIES, normalize_course, parse_date
    if {group['code'] for group in groups} != set(CATEGORIES) or len(groups) != len(CATEGORIES):
        raise CatalogueStorageError('24개 분류가 모두 조회되지 않아 저장하지 않았습니다.')
    if any(group.get('error') for group in groups):
        raise CatalogueStorageError('고용24 조회에 실패한 분야가 있어 기존 저장 자료를 유지했습니다.')
    records, identities = [], set()
    counts = {}
    for group in groups:
        code = group['code']
        items = group['items']
        if len(items) > 20 or (group['available'] > 0 and not items):
            raise CatalogueStorageError('분류별 조회 결과를 확인하지 못해 저장하지 않았습니다.')
        counts[code] = len(items)
        for raw in items:
            identity = tuple(raw.get(key, '') for key in ('trainstCstId', 'trprId', 'trprDegr'))
            if not all(identity) or identity in identities:
                raise CatalogueStorageError('중복되거나 식별 정보가 없는 교육이 있어 저장하지 않았습니다.')
            identities.add(identity)
            course = normalize_course(raw, code)
            records.append((
                *identity, course['title'], course['provider'], course['url'], course['address'],
                course['ncsCode'], parse_date(raw.get('traStartDate')), parse_date(raw.get('traEndDate')),
                raw.get('courseMan', ''), raw.get('realMan', ''), course['mode'], course['modeEvidence'],
                json.dumps(course['tags'], ensure_ascii=False), json.dumps(raw, ensure_ascii=False), code, CATEGORIES[code],
            ))
    if not records:
        raise CatalogueStorageError('교육이 한 건도 조회되지 않아 기존 저장 자료를 유지했습니다.')
    saved_at = datetime.now(timezone.utc)
    with database() as cursor:
        # Transaction-level locking also works with the Supabase pooler.
        cursor.execute('SELECT pg_advisory_xact_lock(214760, 24)')
        cursor.execute('''CREATE TEMPORARY TABLE training_posts_snapshot_keys (
            provider_id text NOT NULL, course_id text NOT NULL, course_round text NOT NULL,
            PRIMARY KEY(provider_id, course_id, course_round)
        ) ON COMMIT DROP''')
        cursor.execute('INSERT INTO training_posts_snapshot_keys VALUES ' + ','.join(['(%s,%s,%s)'] * len(identities)),
                       tuple(value for identity in identities for value in identity))
        values_sql = ','.join(['(' + ','.join(['%s'] * 14 + ['%s::jsonb'] * 2 + ['%s'] * 3) + ')'] * len(records))
        cursor.execute('''INSERT INTO public.training_posts_sms (
            external_provider_id, external_course_id, course_round, title, provider, source_url,
            address, ncs_code, start_date, end_date, course_man_raw, real_man_raw,
            learning_mode, mode_evidence, skills, raw_payload, category_code, category_name, last_seen_at
        ) VALUES ''' + values_sql + '''
        ON CONFLICT (external_provider_id, external_course_id, course_round) DO UPDATE SET
            title=EXCLUDED.title, provider=EXCLUDED.provider, source_url=EXCLUDED.source_url,
            address=EXCLUDED.address, ncs_code=EXCLUDED.ncs_code,
            start_date=EXCLUDED.start_date, end_date=EXCLUDED.end_date,
            course_man_raw=EXCLUDED.course_man_raw, real_man_raw=EXCLUDED.real_man_raw,
            learning_mode=EXCLUDED.learning_mode, mode_evidence=EXCLUDED.mode_evidence,
            skills=EXCLUDED.skills, raw_payload=EXCLUDED.raw_payload,
            category_code=EXCLUDED.category_code, category_name=EXCLUDED.category_name,
            last_seen_at=EXCLUDED.last_seen_at''', tuple(value for record in records for value in (*record, saved_at)))
        # Keep only this table's current 24-category snapshot, atomically with the upserts.
        cursor.execute('''DELETE FROM public.training_posts_sms AS stored WHERE NOT EXISTS (
            SELECT 1 FROM training_posts_snapshot_keys AS current
            WHERE current.provider_id=stored.external_provider_id
              AND current.course_id=stored.external_course_id
              AND current.course_round=stored.course_round)''')
        cursor.execute('SELECT category_code, count(*) FROM public.training_posts_sms GROUP BY category_code')
        if dict(cursor.fetchall()) != {code: count for code, count in counts.items() if count}:
            raise CatalogueStorageError('저장 건수 검증에 실패하여 변경을 취소했습니다.')
    return {'total': len(records), 'categories': counts, 'saved_at': saved_at.isoformat()}
