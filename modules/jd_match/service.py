from typing import List

from psycopg import Connection

# from modules.jd_match.model import TestSejo


# def get_test_rows(db: Connection) -> List[TestSejo]:
#     with db.cursor() as cursor:
#         cursor.execute("SELECT id, created_at FROM public.tests_sejo ORDER BY id")
#         return [TestSejo(**row) for row in cursor.fetchall()]


# 프로필에서 내 역량 가져오기
def get_my_보유역량():
    pass

# jev로 적합도 계산하기
def get_jd_match_score():
    pass

# 공고 상세 내용 가져오기
def get_job_post_detail():
    pass