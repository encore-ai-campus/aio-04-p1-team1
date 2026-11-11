"""public.job_postings를 매개변수화한 SQL로 조회합니다. DB 변경은 수행하지 않습니다."""
from datetime import datetime
from zoneinfo import ZoneInfo
from uuid import UUID
from psycopg import Connection
from .search_models import SearchFilters

JOB_ORDER = ['개발자','데이터 분석가','인사','총무','회계','생산관리','마케팅','기획자']
SORT_SQL = {
    'default': 'j.company_name ASC, j.title ASC, j.id ASC',
    'company': 'j.company_name ASC, j.title ASC, j.id ASC',
    'deadline': 'j.deadline_date ASC NULLS LAST, j.company_name ASC, j.id ASC',
}

def korea_today():
    return datetime.now(ZoneInfo('Asia/Seoul')).date()

def search_condition(filters: SearchFilters):
    conditions, params = ["j.use_yn='Y'"], []
    if filters.q:
        escaped = filters.q.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')
        conditions.append('(j.title ILIKE %s OR j.company_name ILIKE %s OR j.job_name ILIKE %s)')
        params.extend(['%'+escaped+'%']*3)
    if filters.job:
        conditions.append('j.job_name=%s'); params.append(filters.job)
    if filters.region == '수도권':
        conditions.append("split_part(j.region_name,' ',1) IN ('서울','경기','인천')")
    elif filters.region:
        conditions.append("split_part(j.region_name,' ',1)=%s"); params.append(filters.region)
    if filters.career:
        values = {'신입':['신입','신입·경력','무관'], '경력':['경력','신입·경력','무관']}.get(filters.career,[filters.career])
        conditions.append('j.career_type=ANY(%s)'); params.append(values)
    if filters.employment:
        conditions.append('j.employment_type=%s'); params.append(filters.employment)
    if filters.exclude_closed:
        conditions.append('(j.deadline_date IS NULL OR j.deadline_date >= %s)'); params.append(korea_today())
    return ' AND '.join(conditions), params

def get_filter_options(db: Connection):
    with db.cursor() as cursor:
        cursor.execute("""SELECT array_agg(DISTINCT job_name ORDER BY job_name) AS jobs,
            array_agg(DISTINCT split_part(region_name,' ',1) ORDER BY split_part(region_name,' ',1)) AS regions,
            array_agg(DISTINCT employment_type ORDER BY employment_type) FILTER (WHERE employment_type IS NOT NULL) AS employments
            FROM public.job_postings WHERE use_yn='Y'""")
        row = cursor.fetchone()
    jobs = row['jobs'] or []
    return {'jobs': sorted(jobs,key=lambda value: (JOB_ORDER.index(value) if value in JOB_ORDER else len(JOB_ORDER),value)),
            'regions': [value for value in (row['regions'] or []) if value],
            'employments': row['employments'] or []}

def search_jobs(db: Connection, user_id: UUID, filters: SearchFilters):
    condition, params = search_condition(filters)
    today = korea_today()
    # ID/사용자 값은 SQL 문자열에 끼워 넣지 않습니다. 정렬은 고정 허용 목록만 사용합니다.
    with db.cursor() as cursor:
        cursor.execute('SELECT count(*) AS total FROM public.job_postings j WHERE '+condition, params)
        total = cursor.fetchone()['total']
        cursor.execute('''SELECT j.id,j.source_url,j.title,j.company_name,j.job_name,j.region_name,
            j.career_type,j.employment_type,j.min_experience_years,j.max_experience_years,
            j.deadline_type,j.deadline_date,
            EXISTS(SELECT 1 FROM public.saved_jobs s WHERE s.job_id=j.id AND s.user_id=%s AND s.use_yn='Y') AS is_saved,
            COALESCE(j.deadline_date < %s,FALSE) AS is_closed
            FROM public.job_postings j WHERE '''+condition+' ORDER BY '+SORT_SQL[filters.sort]+' LIMIT %s OFFSET %s',
            [user_id,today,*params,filters.size,(filters.page-1)*filters.size])
        items = cursor.fetchall()
    return {'items':items,'total':total,'page':filters.page,'size':filters.size}
