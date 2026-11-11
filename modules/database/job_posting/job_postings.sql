-- public.job_postings의 최종 테이블 설계.
-- 마감 날짜는 처음부터 DATE 타입으로 생성합니다.
-- 신입의 최대 경력 NULL 규칙은 수집·저장 코드에서 적용하고 검증합니다.
CREATE TABLE IF NOT EXISTS public.job_postings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_url text NOT NULL UNIQUE,
    title text NOT NULL,
    company_name text NOT NULL,
    job_name text NOT NULL,
    region_name text NOT NULL,
    employment_type text,
    career_type text,
    min_experience_years integer CHECK (min_experience_years >= 0),
    max_experience_years integer CHECK (max_experience_years >= 0),
    position_detail text,
    main_tasks text,
    qualifications text,
    preferred_qualifications text,
    deadline_type text,
    deadline_date date,
    use_yn char(1) NOT NULL DEFAULT 'Y' CHECK (use_yn IN ('Y', 'N'))
);
ALTER TABLE public.job_postings ENABLE ROW LEVEL SECURITY;
GRANT ALL ON public.job_postings TO service_role;
