from typing import List

from psycopg import Connection

from modules.jd_match.model import TestSejo


def get_test_rows(db: Connection) -> List[TestSejo]:
    with db.cursor() as cursor:
        cursor.execute("SELECT id, created_at FROM public.tests_sejo ORDER BY id")
        return [TestSejo(**row) for row in cursor.fetchall()]
