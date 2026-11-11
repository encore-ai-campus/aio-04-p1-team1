"""공통 회원 헤더·메뉴·A2Z 디자인으로 채용공고 검색 화면을 렌더링합니다."""
from pathlib import Path
from shared.components.compass import apply_member_shell

MODULE_DIR = Path(__file__).resolve().parent

def render_job_search(user):
    html = (MODULE_DIR / 'templates/job_search.html').read_text(encoding='utf-8')
    html = html.replace('__JOB_CSS__',(MODULE_DIR / 'assets/job_search.css').read_text(encoding='utf-8'))
    html = html.replace('__JOB_SCRIPT__',(MODULE_DIR / 'assets/job_search.js').read_text(encoding='utf-8'))
    return apply_member_shell(html,user,current='job_posts')
