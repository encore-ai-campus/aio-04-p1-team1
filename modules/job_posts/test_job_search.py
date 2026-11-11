"""채용 검색의 인증·필터 SQL·페이지 응답 회귀 테스트. 네트워크/DB 연결 없음."""
import unittest
from contextlib import contextmanager
from datetime import date
from unittest.mock import patch
from uuid import UUID
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from psycopg import OperationalError
from pydantic import ValidationError
from shared.auth_dependencies import get_current_user, User
from shared.database import get_db
from .router import router
from .search_models import SearchFilters
from .job_repository import search_condition, search_jobs
from .search_page import render_job_search

USER = User(id=UUID('11111111-1111-4111-8111-111111111111'),name='검증회원',email='test@example.invalid')
ROW = {'id':UUID('22222222-2222-4222-8222-222222222222'),'source_url':'https://www.wanted.co.kr/wd/123',
       'title':'백엔드 개발자','company_name':'검증기업','job_name':'개발자','region_name':'서울 강남구',
       'career_type':'신입','employment_type':'정규직','min_experience_years':0,'max_experience_years':None,
       'deadline_type':'날짜 지정','deadline_date':date(2027,1,1),'is_saved':True,'is_closed':False}

class Cursor:
    def __init__(self): self.calls=[]
    def __enter__(self): return self
    def __exit__(self,*args): pass
    def execute(self,sql,params=None): self.calls.append((sql,params))
    def fetchone(self): return {'total':9}
    def fetchall(self): return [ROW]

class Database:
    def __init__(self): self.current=Cursor()
    def cursor(self): return self.current

class JobSearchTests(unittest.TestCase):
    def app(self,db=None):
        app=FastAPI();app.include_router(router)
        app.dependency_overrides[get_current_user]=lambda:USER
        app.dependency_overrides[get_db]=lambda:db or Database()
        return app

    def test_signed_out_page_redirects(self):
        with patch('modules.job_posts.router.auth_store.authenticated',side_effect=HTTPException(401,'로그인 필요')):
            response=TestClient(self.app()).get('/job_posts',follow_redirects=False)
        self.assertEqual(response.status_code,303)
        self.assertEqual(response.headers['location'],'/signin')

    def test_signed_in_page_reuses_shell_and_escapes_name(self):
        html=render_job_search({'name':'<script>alert(1)</script>'})
        self.assertIn('&lt;script&gt;',html)
        self.assertIn('cc-header',html)
        self.assertNotIn('__CC_',html)
        self.assertNotIn('__JOB_',html)
        self.assertIn('href="/job_posts" aria-current="page"',html)

    def test_api_requires_authentication(self):
        app=self.app()
        def denied(): raise HTTPException(401,'로그인 필요')
        app.dependency_overrides[get_current_user]=denied
        self.assertEqual(TestClient(app).get('/job_posts/api/jobs').status_code,401)

    def test_combined_filters_bind_values_and_escape_wildcards(self):
        filters=SearchFilters(q="SQL%_';--",job='개발자',region='수도권',career='신입',employment='정규직')
        condition,params=search_condition(filters)
        self.assertNotIn(filters.q,condition)
        self.assertIn("SQL\\%\\_';--",params[0])
        self.assertIn(['신입','신입·경력','무관'],params)
        self.assertIn("('서울','경기','인천')",condition)
        self.assertIn('정규직',params)
        self.assertIsInstance(params[-1],date)

    def test_closed_option_and_exact_region(self):
        condition,params=search_condition(SearchFilters(region='부산',exclude_closed=False))
        self.assertNotIn('deadline_date',condition)
        self.assertEqual(params,['부산'])
        self.assertIn("j.use_yn='Y'",condition)

    def test_query_includes_owner_and_stable_pagination(self):
        db=Database()
        result=search_jobs(db,USER.id,SearchFilters(page=2,size=8,sort='deadline'))
        statement,params=db.current.calls[1]
        self.assertEqual(result['total'],9)
        self.assertEqual(params[0],USER.id)
        self.assertEqual(params[-2:],[8,8])
        self.assertIn("s.use_yn='Y'",statement)
        self.assertIn('j.deadline_date ASC NULLS LAST',statement)

    def test_api_returns_card_fields_and_bookmark_state(self):
        response=TestClient(self.app()).get('/job_posts/api/jobs?job=개발자&page=2')
        self.assertEqual(response.status_code,200,response.text)
        body=response.json()
        self.assertEqual(body['page'],2)
        self.assertTrue(body['items'][0]['is_saved'])
        self.assertEqual(body['items'][0]['deadline_date'],'2027-01-01')
        for field in ('company_name','title','job_name','region_name','career_type','employment_type'):
            self.assertIn(field,body['items'][0])

    def test_invalid_query_rejected(self):
        client=TestClient(self.app())
        for query in ('page=0','size=10000','sort=drop_table','career=unknown','q='+'가'*101):
            self.assertEqual(client.get('/job_posts/api/jobs?'+query).status_code,422,query)

    def test_database_error_does_not_expose_connection_details(self):
        with patch('modules.job_posts.router.search_jobs',side_effect=OperationalError('connection secret')):
            response=TestClient(self.app()).get('/job_posts/api/jobs')
        self.assertEqual(response.status_code,503)
        self.assertNotIn('connection secret',response.text)

if __name__=='__main__': unittest.main()
