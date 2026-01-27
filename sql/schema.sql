-- =========================
-- DIMENSIONS
-- =========================
CREATE TABLE IF NOT EXISTS contract (
    id SERIAL PRIMARY KEY,
    type_contrat TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS  industry (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS company (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    raw_name TEXT
);

CREATE TABLE IF NOT EXISTS location (
    id SERIAL PRIMARY KEY,
    ville TEXT NOT NULL,
    code_postal TEXT,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6)
);

-- =========================
-- SKILL
-- =========================
CREATE TABLE IF NOT EXISTS skill (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL
        CHECK (category IN ('hard', 'soft', 'language')),
    UNIQUE (name, category)
);

-- =========================
-- JOB OFFER
-- =========================
CREATE TABLE IF NOT EXISTS job_offer (
    id SERIAL PRIMARY KEY,

    title TEXT NOT NULL,
    description TEXT,

    salary_min_annual TEXT,
    salary_max_annual TEXT,
    experience TEXT,
    education TEXT,

    date_posted DATE,
    url TEXT NOT NULL UNIQUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    contract_id INTEGER REFERENCES contract(id),
    company_id INTEGER REFERENCES company(id),
    industry_id INTEGER REFERENCES industry(id),
    location_id INTEGER REFERENCES location(id)
);

-- =========================
-- JOB OFFER <-> SKILL
-- =========================
CREATE TABLE IF NOT EXISTS job_offer_skill (
    job_offer_id INTEGER REFERENCES job_offer(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skill(id) ON DELETE CASCADE,
    requirement_level TEXT NOT NULL
        CHECK (requirement_level IN ('required', 'optional')),
    PRIMARY KEY (job_offer_id, skill_id)
);

-- =========================
-- INDEXES
-- =========================
CREATE INDEX IF NOT EXISTS idx_job_offer_date ON job_offer(date_posted);
CREATE INDEX IF NOT EXISTS idx_job_offer_company ON job_offer(company_id);
CREATE INDEX IF NOT EXISTS idx_job_offer_location ON job_offer(location_id);
CREATE INDEX IF NOT EXISTS idx_job_offer_skill ON job_offer_skill(skill_id);

-- =========================
-- RESET TABLES
-- =========================
--DROP TABLE IF EXISTS job_offer_skill;
--DROP TABLE IF EXISTS job_offer;
--DROP TABLE IF EXISTS skill;
--DROP TABLE IF EXISTS contract;
--DROP TABLE IF EXISTS industry;
--DROP TABLE IF EXISTS company;
--DROP TABLE IF EXISTS location;