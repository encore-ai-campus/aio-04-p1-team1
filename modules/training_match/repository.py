"""Read selected jobs and only the authenticated member's profile."""
from modules.auth import auth_store
from modules.mypage.profile_api import Profile
from modules.training_posts.repository import database

JOB_COLUMNS = ('id', 'title', 'company_name', 'source_url', 'address', 'employment_type',
               'career_type', 'position_detail', 'main_tasks', 'qualifications',
               'preferred_qualifications', 'status', 'deadline_date')


def _job(row):
    result = dict(zip(JOB_COLUMNS, row))
    result['id'] = str(result['id'])
    result['deadline_date'] = result['deadline_date'].isoformat() if result['deadline_date'] else None
    return result


def list_jobs():
    with database() as cursor:
        cursor.execute('SELECT ' + ','.join(JOB_COLUMNS) + ''' FROM public.job_posting_mj
                       ORDER BY deadline_date DESC NULLS LAST, title, id LIMIT 200''')
        return [_job(row) for row in cursor.fetchall()]


def get_job(job_id):
    with database() as cursor:
        cursor.execute('SELECT ' + ','.join(JOB_COLUMNS) + ' FROM public.job_posting_mj WHERE id=%s::uuid', (str(job_id),))
        row = cursor.fetchone()
    return _job(row) if row else None


def get_own_profile(user, token):
    # Supabase RLS + explicit authenticated user_id filter. Never accept a client user_id.
    rows = auth_store.supabase_request(
        'GET', '/rest/v1/profiles_LYR', token=token,
        params={'select': 'target_role,certificates,courses', 'user_id': 'eq.' + str(user['id']), 'limit': '1'},
    )
    return Profile.model_validate(rows[0]) if rows else None


def profile_summary(profile):
    if profile is None:
        return {'available': False, 'target_role': '', 'certificates': [], 'courses': []}
    return {
        'available': bool(profile.target_role or profile.certificates or profile.courses),
        'target_role': profile.target_role,
        'certificates': [item.name for item in profile.certificates],
        'courses': [item.name for item in profile.courses],
    }
