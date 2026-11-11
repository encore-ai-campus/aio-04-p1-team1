"""프로필 스키마의 실제 권한/RPC 동작 검증. 모든 테스트 데이터는 롤백합니다."""


def verify_runtime(connection):
    import uuid
    import psycopg
    from psycopg.types.json import Jsonb
    checks = {}
    members = [row['user_id'] for row in connection.execute("SELECT user_id FROM public.profiles WHERE use_yn='Y' ORDER BY user_id LIMIT 2").fetchall()]
    checks['name_update_granted'] = connection.execute("SELECT has_column_privilege('authenticated','public.profiles','name','UPDATE') AS ok").fetchone()['ok']
    checks['email_update_denied'] = not connection.execute("SELECT has_column_privilege('authenticated','public.profiles','email','UPDATE') AS ok").fetchone()['ok']
    if not checks['name_update_granted'] or not checks['email_update_denied']:
        raise RuntimeError('프로필 컬럼 권한 검증 실패')
    with connection.transaction(force_rollback=True):
        new_id = uuid.uuid4()
        connection.execute('INSERT INTO auth.users(id,email,raw_user_meta_data) VALUES (%s,%s,%s)',
                           (new_id,f'migration-{new_id.hex}@example.invalid',Jsonb({'name':'가입프로필검증'})))
        created = connection.execute('SELECT name,desired_jobs,skills FROM public.profiles WHERE user_id=%s',(new_id,)).fetchone()
        if not created or created['name']!='가입프로필검증' or created['desired_jobs'] is not None or created['skills'] is not None:
            raise RuntimeError('신규 가입 프로필 생성 트리거 검증 실패')
        checks['signup_trigger'] = True
        # 테스트용 새 계정은 이 SAVEPOINT 종료 시 제거됩니다.
    if not members:
        checks['owner_tests'] = 'skipped_no_profiles'
        return checks
    owner = members[0]
    with connection.transaction(force_rollback=True):
        connection.execute("SELECT set_config('request.jwt.claim.sub',%s,true)",(str(owner),))
        connection.execute('SET LOCAL ROLE authenticated')
        count = connection.execute('SELECT count(*) AS n FROM public.profiles').fetchone()['n']
        if count != 1:
            raise RuntimeError('타인 프로필 조회 차단 검증 실패')
        changed = connection.execute('UPDATE public.profiles SET name=%s WHERE user_id=%s',('수정이름검증',owner)).rowcount
        if changed != 1:
            raise RuntimeError('본인 이름 수정 검증 실패')
        checks['owner_name_update'] = True
        if len(members)>1:
            if connection.execute('UPDATE public.profiles SET name=name WHERE user_id=%s',(members[1],)).rowcount:
                raise RuntimeError('타인 프로필 수정 차단 검증 실패')
            checks['other_user_update_blocked'] = True
        try:
            with connection.transaction():
                connection.execute('UPDATE public.profiles SET email=email WHERE user_id=%s',(owner,))
        except psycopg.errors.InsufficientPrivilege:
            checks['email_update_blocked'] = True
        else:
            raise RuntimeError('이메일 직접 수정이 허용되어 있습니다.')
        call = 'SELECT public.career_compass_save_profile(%s::text[],%s::text[],%s::jsonb,%s::jsonb)'
        connection.execute(call,(['개발자','데이터 분석가'],['Python','SQL'],Jsonb([{'name':'검증자격증','organization':'검증기관','completed_on':'2020-01-01'}]),Jsonb([{'name':'검증교육','organization':'검증기관','completed_on':'2020-01-01'}])))
        profile = connection.execute('SELECT desired_jobs,skills FROM public.profiles WHERE user_id=%s',(owner,)).fetchone()
        if profile['desired_jobs']!=['개발자','데이터 분석가'] or profile['skills']!=['Python','SQL']:
            raise RuntimeError('목록 배열 왕복 저장 검증 실패')
        certificate = connection.execute("SELECT id FROM public.profiles_certifications WHERE user_id=%s AND certification_name='검증자격증' AND use_yn='Y'",(owner,)).fetchone()['id']
        training = connection.execute("SELECT id FROM public.profiles_trainings WHERE user_id=%s AND training_name='검증교육' AND use_yn='Y'",(owner,)).fetchone()['id']
        connection.execute(call,(['개발자'],['Python'],Jsonb([{'id':str(certificate),'name':'수정자격증'}]),Jsonb([])))
        if not connection.execute("SELECT EXISTS(SELECT 1 FROM public.profiles_certifications WHERE id=%s AND certification_name='수정자격증' AND use_yn='Y') AS ok",(certificate,)).fetchone()['ok']:
            raise RuntimeError('이력 UUID 유지 검증 실패')
        if connection.execute('SELECT use_yn FROM public.profiles_trainings WHERE id=%s',(training,)).fetchone()['use_yn']!='N':
            raise RuntimeError('교육 이력 삭제 표시 검증 실패')
        checks['arrays_and_history_rpc'] = True
        try:
            with connection.transaction():
                connection.execute(call,(['실패해야할직무'],[],Jsonb([{'id':str(uuid.uuid4()),'name':'없는자격증'}]),Jsonb([])))
        except psycopg.errors.InsufficientPrivilege:
            if connection.execute('SELECT desired_jobs FROM public.profiles WHERE user_id=%s',(owner,)).fetchone()['desired_jobs']!=['개발자']:
                raise RuntimeError('RPC 실패 시 원자적 롤백 검증 실패')
            checks['rpc_failure_rollback'] = True
        else:
            raise RuntimeError('타인/미등록 이력 ID가 허용되었습니다.')
        try:
            with connection.transaction():
                connection.execute('INSERT INTO public.profiles_certifications(user_id,certification_name) VALUES (%s,%s)',(owner,'   '))
        except psycopg.errors.CheckViolation:
            checks['empty_history_name_blocked'] = True
        else:
            raise RuntimeError('빈 자격증 이름이 허용되었습니다.')
        connection.execute('RESET ROLE')
        connection.execute('UPDATE auth.users SET email=email WHERE id=%s',(owner,))
        if not connection.execute('SELECT name=%s AS ok FROM public.profiles WHERE user_id=%s',('수정이름검증',owner)).fetchone()['ok']:
            raise RuntimeError('Auth 동기화 시 수정한 이름이 보존되지 않았습니다.')
        checks['auth_sync_preserves_name'] = True
        connection.execute('DELETE FROM public.profiles WHERE user_id=%s',(owner,))
        for table in ('profiles_certifications','profiles_trainings','saved_jobs','saved_trainings'):
            if not connection.execute('SELECT to_regclass(%s) IS NOT NULL AS yes', ('public.' + table,)).fetchone()['yes']:
                continue  # 프로필만 생성한 환경에는 북마크 테이블이 없을 수 있습니다.
            if connection.execute(f'SELECT count(*) AS n FROM public.{table} WHERE user_id=%s',(owner,)).fetchone()['n']:
                raise RuntimeError('삭제 연쇄 검증 실패')
        checks['profile_delete_cascade'] = True
    checks['all_test_changes_rolled_back'] = True
    return checks
