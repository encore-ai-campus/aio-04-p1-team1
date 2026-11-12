-- Auth에서 새 프로필을 만들고 이메일만 동기화합니다. 사용자가 수정한 이름은 보존합니다.
CREATE OR REPLACE FUNCTION public.career_compass_sync_auth_profile()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER SET search_path = '' AS $$
BEGIN
    IF NEW.email IS NULL OR NEW.email = '' THEN
        RETURN NEW;
    END IF;
    INSERT INTO public.profiles (user_id, name, email)
    VALUES (NEW.id, COALESCE(NULLIF(btrim(NEW.raw_user_meta_data->>'name'), ''),
                            NULLIF(btrim(NEW.raw_user_meta_data->>'full_name'), ''),
                            NULLIF(btrim(NEW.raw_user_meta_data->>'display_name'), ''), ''), NEW.email)
    ON CONFLICT (user_id) DO UPDATE SET email=EXCLUDED.email,
        name=CASE WHEN btrim(profiles.name)='' THEN EXCLUDED.name ELSE profiles.name END;
    RETURN NEW;
END;
$$;
REVOKE ALL ON FUNCTION public.career_compass_sync_auth_profile() FROM PUBLIC, anon, authenticated;
DROP TRIGGER IF EXISTS career_compass_auth_profile ON auth.users;
CREATE TRIGGER career_compass_auth_profile
    AFTER INSERT OR UPDATE OF email ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.career_compass_sync_auth_profile();

-- JWT로 확인한 본인의 프로필과 여러 이력 변경을 한 트랜잭션으로 저장합니다.
CREATE OR REPLACE FUNCTION public.career_compass_save_profile(
    p_desired_jobs text[], p_skills text[], p_certificates jsonb, p_trainings jsonb
) RETURNS void LANGUAGE plpgsql SECURITY INVOKER SET search_path = '' AS $$
DECLARE
    owner_id uuid := auth.uid();
    item jsonb;
    record_id uuid;
BEGIN
    IF owner_id IS NULL THEN
        RAISE EXCEPTION 'Authentication required' USING ERRCODE='42501';
    END IF;
    IF jsonb_typeof(p_certificates) IS DISTINCT FROM 'array'
       OR jsonb_typeof(p_trainings) IS DISTINCT FROM 'array' THEN
        RAISE EXCEPTION 'History must be JSON arrays' USING ERRCODE='22023';
    END IF;
    IF jsonb_array_length(p_certificates)>50 OR jsonb_array_length(p_trainings)>50
       OR COALESCE(cardinality(p_desired_jobs),0)>20 OR COALESCE(cardinality(p_skills),0)>100
       OR COALESCE(array_ndims(p_desired_jobs),1)>1 OR COALESCE(array_ndims(p_skills),1)>1 THEN
        RAISE EXCEPTION 'Too many profile entries or invalid array dimensions' USING ERRCODE='22023';
    END IF;
    IF EXISTS (SELECT 1 FROM unnest(p_desired_jobs) AS x(value) WHERE value IS NULL OR btrim(value)='' OR length(value)>60)
       OR EXISTS (SELECT 1 FROM unnest(p_skills) AS x(value) WHERE value IS NULL OR btrim(value)='' OR length(value)>100) THEN
        RAISE EXCEPTION 'Invalid job or skill' USING ERRCODE='22023';
    END IF;
    IF (SELECT count(*)<>count(DISTINCT value->>'id') FROM jsonb_array_elements(p_certificates) WHERE NULLIF(value->>'id','') IS NOT NULL)
       OR (SELECT count(*)<>count(DISTINCT value->>'id') FROM jsonb_array_elements(p_trainings) WHERE NULLIF(value->>'id','') IS NOT NULL) THEN
        RAISE EXCEPTION 'Duplicate history IDs' USING ERRCODE='22023';
    END IF;
    UPDATE public.profiles SET desired_jobs=p_desired_jobs, skills=p_skills
    WHERE user_id=owner_id AND use_yn='Y';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Active profile not found' USING ERRCODE='42501';
    END IF;
    UPDATE public.profiles_certifications SET use_yn='N' WHERE user_id=owner_id AND use_yn='Y';
    FOR item IN SELECT value FROM jsonb_array_elements(p_certificates) LOOP
        IF jsonb_typeof(item)<>'object' OR NULLIF(btrim(item->>'name'),'') IS NULL THEN
            RAISE EXCEPTION 'Certificate name required' USING ERRCODE='22023';
        END IF;
        record_id := NULLIF(item->>'id','')::uuid;
        IF record_id IS NULL THEN
            INSERT INTO public.profiles_certifications
                (user_id,certification_name,certification_issuer,certification_acquired_date)
            VALUES (owner_id,btrim(item->>'name'),NULLIF(btrim(item->>'organization'),''),NULLIF(item->>'completed_on','')::date);
        ELSE
            UPDATE public.profiles_certifications SET certification_name=btrim(item->>'name'),
                certification_issuer=NULLIF(btrim(item->>'organization'),''),
                certification_acquired_date=NULLIF(item->>'completed_on','')::date,use_yn='Y'
            WHERE id=record_id AND user_id=owner_id;
            IF NOT FOUND THEN
                RAISE EXCEPTION 'Certificate does not belong to current user' USING ERRCODE='42501';
            END IF;
        END IF;
    END LOOP;
    UPDATE public.profiles_trainings SET use_yn='N' WHERE user_id=owner_id AND use_yn='Y';
    FOR item IN SELECT value FROM jsonb_array_elements(p_trainings) LOOP
        IF jsonb_typeof(item)<>'object' OR NULLIF(btrim(item->>'name'),'') IS NULL THEN
            RAISE EXCEPTION 'Training name required' USING ERRCODE='22023';
        END IF;
        record_id := NULLIF(item->>'id','')::uuid;
        IF record_id IS NULL THEN
            INSERT INTO public.profiles_trainings
                (user_id,training_name,training_provider,training_completed_date)
            VALUES (owner_id,btrim(item->>'name'),NULLIF(btrim(item->>'organization'),''),NULLIF(item->>'completed_on','')::date);
        ELSE
            UPDATE public.profiles_trainings SET training_name=btrim(item->>'name'),
                training_provider=NULLIF(btrim(item->>'organization'),''),
                training_completed_date=NULLIF(item->>'completed_on','')::date,use_yn='Y'
            WHERE id=record_id AND user_id=owner_id;
            IF NOT FOUND THEN
                RAISE EXCEPTION 'Training does not belong to current user' USING ERRCODE='42501';
            END IF;
        END IF;
    END LOOP;
END;
$$;
REVOKE ALL ON FUNCTION public.career_compass_save_profile(text[],text[],jsonb,jsonb) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.career_compass_save_profile(text[],text[],jsonb,jsonb) TO authenticated, service_role;
NOTIFY pgrst, 'reload schema';
