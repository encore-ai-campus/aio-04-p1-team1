DO $schema$
BEGIN
    IF to_regclass('public.training_posting') IS NULL THEN
        CREATE TABLE public.training_posting (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            work24_training_id text NOT NULL,
            source_url text NOT NULL UNIQUE,
            title text NOT NULL,
            center_name text,
            center_address text,
            training_start_dt date,
            training_end_dt date,
            use_yn char(1) NOT NULL DEFAULT 'Y' CHECK (use_yn IN ('Y', 'N'))
        );
        ALTER TABLE public.training_posting ENABLE ROW LEVEL SECURITY;
    END IF;
    -- 기존 테이블은 데이터를 다시 넣지 않고 외부 과정 ID 컬럼명만 바꿉니다.
    IF EXISTS (SELECT 1 FROM information_schema.columns
        WHERE table_schema='public' AND table_name='training_posting' AND column_name='training_id') THEN
        IF EXISTS (SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='training_posting' AND column_name='work24_training_id') THEN
            RAISE EXCEPTION 'Both training_id and work24_training_id exist; resolve before migration';
        END IF;
        ALTER TABLE public.training_posting RENAME COLUMN training_id TO work24_training_id;
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'training_posting'
          AND column_name = 'training_start_dt' AND data_type = 'date'
    ) THEN
        RAISE EXCEPTION 'Existing training_posting schema differs; no columns were removed';
    END IF;
END;
$schema$;
