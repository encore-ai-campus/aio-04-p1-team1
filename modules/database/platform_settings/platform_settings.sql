-- 플랫폼별 사용자 설정. profiles 생성 후 실행합니다.
-- user_email은 사용자가 플랫폼별 수신용으로 직접 입력하는 이메일입니다.
-- profiles.email이나 Auth 계정 이메일에서 가져오거나 동기화하지 않습니다.
CREATE TABLE IF NOT EXISTS public.platform_settings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES public.profiles(user_id) ON DELETE CASCADE,
    platform_name text NOT NULL CHECK (btrim(platform_name) <> ''),
    platform_email text NOT NULL CHECK (btrim(platform_email) <> ''),
    user_email text NOT NULL CHECK (btrim(user_email) <> ''),
    use_yn char(1) NOT NULL DEFAULT 'Y' CHECK (use_yn IN ('Y', 'N')),
    created_at timestamptz NOT NULL DEFAULT now()
);

COMMENT ON COLUMN public.platform_settings.user_email
    IS '사용자가 해당 플랫폼의 수신용으로 직접 입력한 이메일';

CREATE INDEX IF NOT EXISTS platform_settings_user_id_idx
    ON public.platform_settings (user_id);

ALTER TABLE public.platform_settings ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON public.platform_settings FROM PUBLIC, anon, authenticated;
GRANT ALL ON public.platform_settings TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.platform_settings TO authenticated;

DROP POLICY IF EXISTS career_compass_own_select ON public.platform_settings;
CREATE POLICY career_compass_own_select ON public.platform_settings
    FOR SELECT TO authenticated USING ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS career_compass_own_insert ON public.platform_settings;
CREATE POLICY career_compass_own_insert ON public.platform_settings
    FOR INSERT TO authenticated WITH CHECK ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS career_compass_own_update ON public.platform_settings;
CREATE POLICY career_compass_own_update ON public.platform_settings
    FOR UPDATE TO authenticated USING ((SELECT auth.uid()) = user_id)
    WITH CHECK ((SELECT auth.uid()) = user_id);

DROP POLICY IF EXISTS career_compass_own_delete ON public.platform_settings;
CREATE POLICY career_compass_own_delete ON public.platform_settings
    FOR DELETE TO authenticated USING ((SELECT auth.uid()) = user_id);
