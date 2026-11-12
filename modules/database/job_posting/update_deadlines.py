"""한국 날짜 기준 마감일이 지난 채용공고를 비활성화합니다.

python -m modules.database.job_posting.update_deadlines --dry-run
python -m modules.database.job_posting.update_deadlines
"""
import argparse
from contextlib import contextmanager

from shared.database import get_db

UPDATE_SQL = """UPDATE public.job_postings
SET use_yn='N'
WHERE use_yn='Y' AND deadline_date IS NOT NULL
  AND (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Seoul')::date > deadline_date"""


def update_deadlines(db):
    """호출자가 관리하는 트랜잭션에서 갱신하고 변경된 행 수를 반환합니다."""
    with db.cursor() as cursor:
        cursor.execute(UPDATE_SQL)
        return cursor.rowcount


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='갱신 대상 건수만 확인하고 변경 롤백')
    args = parser.parse_args()
    try:
        with contextmanager(get_db)() as db:
            with db.transaction(force_rollback=args.dry_run):
                count = update_deadlines(db)
        print(f'{"검증 후 롤백" if args.dry_run else "갱신 완료"}: {count}건')
    except Exception as exc:
        parser.exit(1, f'마감 상태 갱신 실패: {type(exc).__name__} (접속정보는 출력하지 않습니다.)\n')


if __name__ == '__main__':
    main()
