DO $schema$
BEGIN
    IF to_regclass('public.training_posting_mj') IS NULL THEN
        CREATE TABLE public.training_posting_mj (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            training_id text NOT NULL,
            source_url text NOT NULL UNIQUE,
            title text NOT NULL,
            center_name text,
            center_address text,
            training_start_dt date,
            training_end_dt date,
            use_yn char(1) NOT NULL DEFAULT 'Y' CHECK (use_yn IN ('Y', 'N'))
        );
        ALTER TABLE public.training_posting_mj ENABLE ROW LEVEL SECURITY;
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'training_posting_mj'
          AND column_name = 'training_start_dt' AND data_type = 'date'
    ) THEN
        RAISE EXCEPTION 'Existing training_posting_mj schema differs; no columns were removed';
    END IF;
END;
$schema$;
