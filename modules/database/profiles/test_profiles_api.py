"""프로필 API 전환 회귀 테스트. 네트워크와 실제 DB를 사용하지 않습니다."""

import unittest
from unittest.mock import patch
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import ValidationError

from modules.auth import auth_store
from modules.mypage import profile_api
from modules.database.profiles import table as profile_tables

USER_ID = '11111111-1111-4111-8111-111111111111'
CERT_ID = '22222222-2222-4222-8222-222222222222'
TRAIN_ID = '33333333-3333-4333-8333-333333333333'
MEMBER = ({'id': USER_ID, 'name': '기존이름', 'email': 'member@example.invalid'}, 'test-token')


def profile_row():
    return {'desired_jobs': ['개발자','데이터 분석가'], 'skills':['Python','SQL'],
            'profiles_certifications':[{'id':CERT_ID,'certification_name':'정보처리기사','certification_issuer':'발급기관','certification_acquired_date':'2020-01-01','use_yn':'Y'}],
            'profiles_trainings':[{'id':TRAIN_ID,'training_name':'교육이력','training_provider':None,'training_completed_date':None,'use_yn':'N'}]}


class ProfilesAPITests(unittest.TestCase):
    def test_final_schema_does_not_depend_on_legacy_users(self):
        sql = profile_tables.schema_sql()
        self.assertIn('REFERENCES auth.users(id)',sql)
        self.assertNotIn('public.users',sql)
        self.assertNotIn('DROP TABLE',sql)
        self.assertNotIn('ALTER COLUMN',sql)

    def test_isolated_schema_names_and_inactive_access_policy(self):
        names = {'profiles':'profiles2','profiles_certifications':'profiles2_certifications','profiles_trainings':'profiles_trainings'}
        sql = profile_tables.schema_sql(schema='profile_test',table_names=names)
        self.assertIn('REFERENCES profile_test.profiles2(user_id)',sql)
        self.assertIn('profile_test.profiles_trainings',sql)
        access = profile_tables.access_sql(schema='profile_test',table_names=names)
        self.assertIn("p.use_yn='Y'",access)
        with self.assertRaises(ValueError):
            profile_tables.schema_sql(schema='public; DROP SCHEMA public')

    def test_login_reads_name_from_profiles(self):
        auth = {'id':USER_ID,'email':'auth@example.invalid','email_confirmed_at':'2020-01-01'}
        with patch.object(auth_store,'supabase_request',return_value=[{'user_id':USER_ID,'name':'수정이름','email':'member@example.invalid','use_yn':'Y'}]) as request:
            result = auth_store.profile(auth,'test-token')
        self.assertEqual(result['name'],'수정이름')
        self.assertEqual(request.call_args.args,('GET','/rest/v1/profiles'))
        self.assertEqual(request.call_args.kwargs['params']['user_id'],'eq.'+USER_ID)

    def test_disabled_profile_cannot_login(self):
        with patch.object(auth_store,'supabase_request',return_value=[{'user_id':USER_ID,'name':'중지','email':'member@example.invalid','use_yn':'N'}]):
            with self.assertRaises(HTTPException) as context:
                auth_store.profile({'id':USER_ID,'email_confirmed_at':'2020-01-01'},'test-token')
        self.assertEqual(context.exception.status_code,403)

    def test_screen_name_patch_updates_profiles_with_owner_filter(self):
        app = FastAPI(); app.include_router(auth_store.api)
        with patch.object(auth_store,'authenticated',return_value=MEMBER), patch.object(auth_store,'supabase_request',return_value=[{'user_id':USER_ID,'name':'새이름'}]) as request:
            response = TestClient(app).patch('/api/auth/me',json={'name':'새이름'})
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()['name'],'새이름')
        self.assertEqual(request.call_args.args,('PATCH','/rest/v1/profiles'))
        self.assertEqual(request.call_args.kwargs['json'],{'name':'새이름'})
        self.assertEqual(request.call_args.kwargs['params']['user_id'],'eq.'+USER_ID)

    def test_empty_name_and_email_edit_payload_rejected(self):
        app = FastAPI(); app.include_router(auth_store.api)
        with patch.object(auth_store,'supabase_request') as request:
            client = TestClient(app)
            for payload in [{'name':'   '},{'name':'새이름','email':'other@example.invalid'}]:
                self.assertEqual(client.patch('/api/auth/me',json=payload).status_code,422)
            request.assert_not_called()

    def test_nested_history_mapping_and_deleted_history_filtered(self):
        with patch.object(auth_store,'supabase_request',return_value=[profile_row()]):
            result = profile_api.get_profile(MEMBER)
        self.assertEqual(result.desired_jobs,['개발자','데이터 분석가'])
        self.assertEqual(result.skills,['Python','SQL'])
        self.assertEqual(result.target_role,'개발자, 데이터 분석가')
        self.assertEqual(result.certificates[0].id,UUID(CERT_ID))
        self.assertEqual(result.courses,[])

    def test_history_save_uses_one_atomic_rpc_and_preserves_ids(self):
        body = profile_api.Profile(desired_jobs=['개발자'],skills=['Python'],certificates=[{'id':CERT_ID,'name':'정보처리기사'}])
        with patch.object(auth_store,'supabase_request',side_effect=[None,[profile_row()]]) as request:
            profile_api.save_profile(body,MEMBER)
        first = request.call_args_list[0]
        self.assertEqual(first.args,('POST','/rest/v1/rpc/career_compass_save_profile'))
        self.assertEqual(first.kwargs['token'],'test-token')
        self.assertEqual(first.kwargs['json']['p_certificates'][0]['id'],CERT_ID)
        self.assertNotIn('user_id',first.kwargs['json'])
        self.assertEqual(request.call_args_list[1].args,('GET','/rest/v1/profiles'))

    def test_legacy_role_field_converted_to_list(self):
        body = profile_api.Profile(target_role='개발자, 기획자')
        with patch.object(auth_store,'supabase_request',side_effect=[None,[profile_row()]]) as request:
            profile_api.save_profile(body,MEMBER)
        self.assertEqual(request.call_args_list[0].kwargs['json']['p_desired_jobs'],['개발자','기획자'])

    def test_rpc_failure_does_not_continue_with_individual_writes(self):
        with patch.object(auth_store,'supabase_request',side_effect=HTTPException(status_code=503)) as request:
            with self.assertRaises(HTTPException):
                profile_api.save_profile(profile_api.Profile(),MEMBER)
        self.assertEqual(request.call_count,1)

    def test_lists_and_duplicate_record_ids_validated(self):
        for payload in [{'desired_jobs':'개발자'}, {'skills':['   ']},
                        {'certificates':[{'id':CERT_ID,'name':'가'},{'id':CERT_ID,'name':'나'}]},
                        {'user_id':USER_ID}]:
            with self.subTest(payload=payload), self.assertRaises(ValidationError):
                profile_api.Profile.model_validate(payload)


if __name__=='__main__':
    unittest.main()
