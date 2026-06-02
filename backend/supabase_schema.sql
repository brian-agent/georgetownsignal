-- ================================================================
-- Georgetown Signal v2 — Supabase Schema
-- Run in: Supabase → SQL Editor → New Query → Run All
-- ================================================================

-- ── Extensions ──────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ================================================================
-- VENDOR PROFILES
-- Linked 1:1 to Supabase auth.users via supabase_uid
-- ================================================================
CREATE TABLE IF NOT EXISTS vendor_profiles (
    id              BIGSERIAL PRIMARY KEY,
    supabase_uid    UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    email           TEXT NOT NULL,
    full_name       TEXT DEFAULT '',
    phone           TEXT DEFAULT '',
    plan            TEXT DEFAULT 'free' CHECK (plan IN ('free','starter','pro','featured')),
    onboarding_done BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ================================================================
-- BUSINESSES
-- A vendor can own one or more business listings
-- ================================================================
CREATE TABLE IF NOT EXISTS businesses (
    id                  BIGSERIAL PRIMARY KEY,
    vendor_id           BIGINT REFERENCES vendor_profiles(id) ON DELETE SET NULL,
    supabase_uid        UUID REFERENCES auth.users(id) ON DELETE SET NULL,

    -- Core info
    name                TEXT NOT NULL,
    slug                TEXT UNIQUE NOT NULL,
    category            TEXT NOT NULL,
    category_slug       TEXT NOT NULL,
    description         TEXT DEFAULT '',
    phone               TEXT DEFAULT '',
    website             TEXT DEFAULT '',
    address             TEXT DEFAULT '',
    city                TEXT DEFAULT 'Georgetown',
    state               TEXT DEFAULT 'TX',

    -- Trust flags (explicit booleans — set by admin or auto-computed)
    is_verified         BOOLEAN DEFAULT FALSE,   -- admin grants after vetting
    is_featured         BOOLEAN DEFAULT FALSE,   -- paid upgrade
    is_responsive       BOOLEAN DEFAULT FALSE,   -- auto: avg_response_minutes < 45
    is_community_trusted BOOLEAN DEFAULT FALSE,  -- auto: mention_count >= 10

    -- Computed trust metrics (updated by Celery tasks)
    reliability_score   INTEGER DEFAULT 0 CHECK (reliability_score BETWEEN 0 AND 100),
    avg_response_minutes INTEGER DEFAULT NULL,   -- raw minutes, derived from CallAnchor
    avg_response_time   TEXT DEFAULT '—',        -- human display e.g. "22 min"
    mention_count       INTEGER DEFAULT 0,
    jobs_completed      INTEGER DEFAULT 0,

    -- CallAnchor integration
    callanchor_enabled  BOOLEAN DEFAULT FALSE,
    callanchor_phone    TEXT DEFAULT '',
    callanchor_score    INTEGER DEFAULT NULL,

    -- Admin / status
    is_active           BOOLEAN DEFAULT TRUE,
    is_pending_review   BOOLEAN DEFAULT TRUE,    -- new signups await admin approval
    rejection_reason    TEXT DEFAULT '',

    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_biz_category    ON businesses(category_slug);
CREATE INDEX idx_biz_score       ON businesses(reliability_score DESC);
CREATE INDEX idx_biz_city        ON businesses(city, state);
CREATE INDEX idx_biz_vendor      ON businesses(vendor_id);
CREATE INDEX idx_biz_active      ON businesses(is_active, is_pending_review);

-- ================================================================
-- SIGNALS
-- ================================================================
CREATE TABLE IF NOT EXISTS signals (
    id            BIGSERIAL PRIMARY KEY,
    business_id   BIGINT REFERENCES businesses(id) ON DELETE SET NULL,
    business_name TEXT DEFAULT '',
    service       TEXT NOT NULL,
    mentions      INTEGER DEFAULT 1,
    source        TEXT NOT NULL,
    source_url    TEXT DEFAULT '',
    raw_text      TEXT DEFAULT '',
    sentiment     TEXT NOT NULL CHECK (sentiment IN ('positive','neutral','negative','request')),
    city          TEXT DEFAULT 'Georgetown',
    state         TEXT DEFAULT 'TX',
    processed     BOOLEAN DEFAULT FALSE,
    timestamp     TIMESTAMPTZ NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_signal_city      ON signals(city, state);
CREATE INDEX idx_signal_timestamp ON signals(timestamp DESC);
CREATE INDEX idx_signal_processed ON signals(processed);

-- ================================================================
-- REVIEWS
-- ================================================================
CREATE TABLE IF NOT EXISTS reviews (
    id          BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    author_name TEXT NOT NULL,
    text        TEXT NOT NULL,
    sentiment   TEXT DEFAULT 'positive' CHECK (sentiment IN ('positive','neutral','negative')),
    source      TEXT DEFAULT 'Community',
    source_url  TEXT DEFAULT '',
    from_signal BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_review_business ON reviews(business_id);

-- ================================================================
-- LEADS (service requests from residents)
-- ================================================================
CREATE TABLE IF NOT EXISTS leads (
    id              BIGSERIAL PRIMARY KEY,
    category        TEXT NOT NULL,
    description     TEXT NOT NULL,
    budget          TEXT DEFAULT '',
    contact         TEXT NOT NULL,
    urgency         TEXT DEFAULT 'normal' CHECK (urgency IN ('normal','urgent','emergency')),
    city            TEXT DEFAULT 'Georgetown',
    state           TEXT DEFAULT 'TX',
    status          TEXT DEFAULT 'new' CHECK (status IN ('new','notified','matched','closed')),
    assigned_biz_id BIGINT REFERENCES businesses(id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_lead_status   ON leads(status);
CREATE INDEX idx_lead_category ON leads(category);

-- ================================================================
-- NEWSLETTER SUBSCRIBERS
-- ================================================================
CREATE TABLE IF NOT EXISTS newsletter_subscribers (
    id         BIGSERIAL PRIMARY KEY,
    email      TEXT UNIQUE NOT NULL,
    city       TEXT DEFAULT 'Georgetown',
    state      TEXT DEFAULT 'TX',
    is_active  BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ================================================================
-- NEWS POSTS
-- ================================================================
CREATE TABLE IF NOT EXISTS news_posts (
    id                    BIGSERIAL PRIMARY KEY,
    title                 TEXT NOT NULL,
    slug                  TEXT UNIQUE NOT NULL,
    excerpt               TEXT NOT NULL,
    content_md            TEXT NOT NULL,
    category              TEXT NOT NULL,
    article_type          TEXT DEFAULT 'local_news'
                          CHECK (article_type IN ('service_provider','demand_report','community','warning','local_news')),
    service_category_slug TEXT DEFAULT '',
    tags                  JSONB DEFAULT '[]',
    read_time_minutes     INTEGER DEFAULT 3,
    demand_snapshot       JSONB DEFAULT NULL,
    published_at          TIMESTAMPTZ NOT NULL,
    is_published          BOOLEAN DEFAULT FALSE,
    created_at            TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_news_pub ON news_posts(published_at DESC) WHERE is_published = TRUE;

-- ================================================================
-- ROW LEVEL SECURITY
-- ================================================================

-- vendor_profiles: owner reads/writes their own row; service role bypasses
ALTER TABLE vendor_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "vendor_select_own" ON vendor_profiles
    FOR SELECT USING (auth.uid() = supabase_uid);

CREATE POLICY "vendor_update_own" ON vendor_profiles
    FOR UPDATE USING (auth.uid() = supabase_uid);

-- businesses: public reads active listings; vendor manages own listing
ALTER TABLE businesses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "public_read_businesses" ON businesses
    FOR SELECT USING (is_active = TRUE AND is_pending_review = FALSE);

CREATE POLICY "vendor_insert_business" ON businesses
    FOR INSERT WITH CHECK (auth.uid() = supabase_uid);

CREATE POLICY "vendor_update_own_business" ON businesses
    FOR UPDATE USING (auth.uid() = supabase_uid);

-- reviews, signals, news: public read
ALTER TABLE reviews  ENABLE ROW LEVEL SECURITY;
ALTER TABLE signals  ENABLE ROW LEVEL SECURITY;
ALTER TABLE news_posts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "public_read_reviews"    ON reviews    FOR SELECT USING (TRUE);
CREATE POLICY "public_read_signals"    ON signals    FOR SELECT USING (TRUE);
CREATE POLICY "public_read_news"       ON news_posts FOR SELECT USING (is_published = TRUE);

-- leads, newsletter: insert by anyone; read by service role only
ALTER TABLE leads                  ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_subscribers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "anyone_insert_lead" ON leads
    FOR INSERT WITH CHECK (TRUE);

CREATE POLICY "anyone_insert_newsletter" ON newsletter_subscribers
    FOR INSERT WITH CHECK (TRUE);

-- ================================================================
-- TRIGGER: auto-update updated_at
-- ================================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_vendor_updated_at
    BEFORE UPDATE ON vendor_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_biz_updated_at
    BEFORE UPDATE ON businesses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ================================================================
-- TRIGGER: auto-create vendor_profile on signup
-- ================================================================
CREATE OR REPLACE FUNCTION handle_new_vendor()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.vendor_profiles (supabase_uid, email)
    VALUES (NEW.id, NEW.email)
    ON CONFLICT (supabase_uid) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_vendor_signup
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION handle_new_vendor();

-- ================================================================
-- SEED DATA
-- ================================================================
INSERT INTO businesses
    (name, slug, category, category_slug, description, phone,
     reliability_score, avg_response_minutes, avg_response_time,
     mention_count, is_verified, is_responsive, is_community_trusted,
     is_active, is_pending_review)
VALUES
    ('Bright Electric','bright-electric','Electricians','electricians',
     'Family-run electrical contractors serving Georgetown for 12 years.',
     '512-555-0182', 94, 22,'22 min',47, TRUE,TRUE,TRUE, TRUE,FALSE),

    ('Metro Pipes','metro-pipes','Plumbers','plumbers',
     'Licensed plumbers covering Georgetown 24/7.',
     '512-555-0271', 89, 35,'35 min',31, TRUE,TRUE,TRUE, TRUE,FALSE),

    ('AZ Roofing Co.','az-roofing-co','Roofers','roofers',
     'Full-service roofing — repair, replacement, storm damage.',
     '512-555-0349', 87, 120,'2 hrs',28, TRUE,FALSE,TRUE, TRUE,FALSE),

    ('ClearHome Cleaners','clearhome-cleaners','Cleaners','cleaners',
     'Residential and commercial cleaning. Move-in/out specialists.',
     '512-555-0418', 91, 2880,'48 hrs',22, FALSE,FALSE,TRUE, TRUE,FALSE),

    ('Comfort Air TX','comfort-air-tx','HVAC','hvac',
     'HVAC installation, repair, and maintenance. Georgetown TX.',
     '512-555-0502', 85, 60,'1 hr',18, TRUE,TRUE,FALSE, TRUE,FALSE)
ON CONFLICT (slug) DO NOTHING;
