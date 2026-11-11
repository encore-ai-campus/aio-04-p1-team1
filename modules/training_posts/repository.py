"""public.training_posting access. Course data is read from DB, never from the browser."""
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
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
                cursor.execute("SET TRANSACTION READ ONLY")
                cursor.execute("SET LOCAL statement_timeout = '30s'")
                yield cursor
    except CatalogueStorageError:
        raise
    except Exception as exc:
        LOGGER.warning('Training catalogue database operation failed (%s)', type(exc).__name__)
        raise CatalogueStorageError('교육 저장소에 연결하지 못했습니다. 잠시 후 다시 확인해 주세요.') from None


def read_catalogue(start, end):
    """Read the existing shared table without changing its schema or data."""
    from modules.training_posts.service import normalize_stored_course

    with database() as cursor:
        cursor.execute('''SELECT id, work24_training_id, source_url, title, center_name,
                                 center_address, training_start_dt, training_end_dt
                          FROM public.training_posting
                          WHERE use_yn = 'Y'
                            AND (training_start_dt BETWEEN %s AND %s
                                 OR training_start_dt IS NULL)
                          ORDER BY training_start_dt DESC NULLS LAST, title, id''', (start, end))
        rows = cursor.fetchall()
    return {
        'courses': [normalize_stored_course(row) for row in rows],
        'categories': [{'code': 'unknown', 'name': '분야 미제공'}],
        'errors': [], 'source': 'supabase',
        'fetchedAt': datetime.now(KST).strftime('%Y-%m-%d %H:%M:%S'),
        'start': start.isoformat(), 'end': end.isoformat(),
    }
