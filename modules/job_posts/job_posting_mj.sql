-- public.job_posting_mj: 날짜를 DATE 타입으로 저장합니다.
DO $schema$
BEGIN
    IF to_regclass('public.job_posting_mj') IS NULL THEN
        CREATE TABLE public.job_posting_mj (
            id uuid PRIMARY KEY,
            source_url text NOT NULL UNIQUE,
            title text NOT NULL,
            company_name text NOT NULL,
            region_id uuid,
            address text,
            employment_type text,
            career_type text NOT NULL,
            min_experience_months integer CHECK (min_experience_months >= 0),
            max_experience_months integer CHECK (max_experience_months >= 0),
            position_detail text,
            main_tasks text,
            qualifications text,
            preferred_qualifications text,
            deadline_type text NOT NULL,
            deadline_date date,
            status text NOT NULL,
            CHECK (min_experience_months <= max_experience_months)
        );
        ALTER TABLE public.job_posting_mj ENABLE ROW LEVEL SECURITY;
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'job_posting_mj'
          AND column_name = 'deadline_date' AND data_type = 'date'
    ) THEN
        RAISE EXCEPTION 'public.job_posting_mj.deadline_date must have DATE type';
    END IF;
END;
$schema$;
