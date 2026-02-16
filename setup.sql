-- ================================================
-- Social Profiles App — Database Setup
-- ================================================

-- Step 1: Create the database (run as superuser)
-- CREATE DATABASE social_profiles;

-- Step 2: Run this script in the social_profiles database

-- ------------------------------------------------
-- OPTION A: Fresh table (if you haven't loaded data yet)
-- ------------------------------------------------
CREATE TABLE IF NOT EXISTS public.social_profiles (
    id                      SERIAL PRIMARY KEY,
    zone                    VARCHAR(200),
    party_district          VARCHAR(200),
    constituency            VARCHAR(200),
    designation             VARCHAR(200),
    name                    VARCHAR(500),
    whatsapp_number         VARCHAR(50),
    dob                     VARCHAR(50),
    address                 TEXT,
    email_id                VARCHAR(500),
    facebook_id             VARCHAR(500),
    facebook_followers      BIGINT,
    facebook_active_status  VARCHAR(50),
    facebook_verified_status VARCHAR(50),
    twitter_id              VARCHAR(500),
    twitter_followers       BIGINT,
    twitter_active_status   VARCHAR(50),
    twitter_verified_status VARCHAR(50),
    instagram_id            VARCHAR(500),
    instagram_followers     BIGINT,
    instagram_active_status  VARCHAR(50),
    instagram_verified_status VARCHAR(50),
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at              TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ------------------------------------------------
-- OPTION B: Alter existing table to add id + timestamps
-- (if you already loaded data via the COPY command)
-- ------------------------------------------------
-- Run these if your table exists but has no id column:
-- ALTER TABLE public.social_profiles ADD COLUMN IF NOT EXISTS id SERIAL;
-- UPDATE public.social_profiles SET id = nextval('social_profiles_id_seq') WHERE id IS NULL;
-- ALTER TABLE public.social_profiles ADD PRIMARY KEY (id);
-- ALTER TABLE public.social_profiles ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
-- ALTER TABLE public.social_profiles ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- ------------------------------------------------
-- Indexes for fast filtering & search
-- ------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_sp_zone            ON public.social_profiles (zone);
CREATE INDEX IF NOT EXISTS idx_sp_party_district  ON public.social_profiles (party_district);
CREATE INDEX IF NOT EXISTS idx_sp_constituency    ON public.social_profiles (constituency);
CREATE INDEX IF NOT EXISTS idx_sp_designation     ON public.social_profiles (designation);
CREATE INDEX IF NOT EXISTS idx_sp_name            ON public.social_profiles (name);
CREATE INDEX IF NOT EXISTS idx_sp_fb_followers    ON public.social_profiles (facebook_followers DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_sp_tw_followers    ON public.social_profiles (twitter_followers DESC NULLS LAST);
CREATE INDEX IF NOT EXISTS idx_sp_ig_followers    ON public.social_profiles (instagram_followers DESC NULLS LAST);

-- Full-text search index
CREATE INDEX IF NOT EXISTS idx_sp_fts ON public.social_profiles
    USING GIN (to_tsvector('english', coalesce(name,'') || ' ' || coalesce(constituency,'') || ' ' || coalesce(designation,'')));

-- ------------------------------------------------
-- Auto-update updated_at on row changes
-- ------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_updated_at ON public.social_profiles;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON public.social_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ------------------------------------------------
-- Load your CSV (adjust path as needed)
-- ------------------------------------------------
-- COPY public.social_profiles (
--     zone, party_district, constituency, designation, name,
--     whatsapp_number, dob, address, email_id,
--     facebook_id, facebook_followers, facebook_active_status, facebook_verified_status,
--     twitter_id, twitter_followers, twitter_active_status, twitter_verified_status,
--     instagram_id, instagram_followers, instagram_active_status, instagram_verified_status
-- )
-- FROM 'C:\social_profiles_25000.csv'
-- DELIMITER ',' CSV HEADER;
