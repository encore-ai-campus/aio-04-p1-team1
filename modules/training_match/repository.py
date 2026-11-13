"""Read the shared job table used by the listing and fit analysis."""
from modules.training_posts.repository import database

JOB_COLUMNS = ("id", "title", "company_name", "job_name", "deadline_date")


def _job(row):
    result = dict(zip(JOB_COLUMNS, row))
    result["id"] = str(result["id"])
    result["deadline_date"] = result["deadline_date"].isoformat() if result["deadline_date"] else None
    return result


def list_jobs():
    with database() as cursor:
        cursor.execute("SELECT " + ",".join(JOB_COLUMNS) + """ FROM public.job_postings
                       WHERE use_yn = 'Y'
                       ORDER BY deadline_date ASC NULLS LAST, title, id""")
        return [_job(row) for row in cursor.fetchall()]


def get_job(job_id):
    with database() as cursor:
        cursor.execute("SELECT " + ",".join(JOB_COLUMNS) + """ FROM public.job_postings
                       WHERE id=%s::uuid AND use_yn IN ('Y', 'N')""", (str(job_id),))
        row = cursor.fetchone()
    return _job(row) if row else None
