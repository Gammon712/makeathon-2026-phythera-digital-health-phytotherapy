-- PhyThera reference schema
-- PostgreSQL / Supabase
-- This schema contains structure only: no credentials and no source-derived data.
-- RLS policies are intentionally deployment-specific. See rls_demo_readonly.sql.

create extension if not exists pgcrypto;

create table if not exists plants (
    id uuid primary key default gen_random_uuid(),
    scientific_name text not null unique,
    family text,
    common_names text[] not null default '{}',
    description text,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists plant_names (
    id uuid primary key default gen_random_uuid(),
    plant_id uuid not null references plants(id) on delete cascade,
    name text not null,
    language_code text,
    name_type text not null default 'synonym'
        check (name_type in ('scientific','common','traditional','synonym')),
    traditional_system text,
    created_at timestamptz not null default now(),
    unique (plant_id, name, name_type, traditional_system)
);

create table if not exists indications (
    id uuid primary key default gen_random_uuid(),
    normalized_term text not null unique,
    display_name text not null,
    synonyms text[] not null default '{}',
    icd11_code text,
    description text,
    created_at timestamptz not null default now()
);

create table if not exists sources (
    id uuid primary key default gen_random_uuid(),
    source_type text not null
        check (source_type in (
            'ema','who','tcm','consensus','original_paper','pubmed',
            'pubchem','product_registry','pharmacopoeia',
            'herbal_database','other'
        )),
    title text not null,
    authors text[],
    publication_year integer,
    journal text,
    doi text,
    external_id text,
    url text,
    accessed_at timestamptz not null default now(),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists preparations (
    id uuid primary key default gen_random_uuid(),
    plant_id uuid not null references plants(id) on delete cascade,
    plant_part text,
    preparation_type text,
    extraction_solvent text,
    der text,
    formulation text,
    details jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists constituents (
    id uuid primary key default gen_random_uuid(),
    name text not null unique,
    compound_group text,
    pubchem_cid text,
    description text,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists plant_constituents (
    id uuid primary key default gen_random_uuid(),
    plant_id uuid not null references plants(id) on delete cascade,
    constituent_id uuid not null references constituents(id) on delete cascade,
    source_id uuid references sources(id) on delete set null,
    plant_part text,
    proposed_role text,
    evidence_note text,
    created_at timestamptz not null default now()
);

create table if not exists evidence_records (
    id uuid primary key default gen_random_uuid(),
    plant_id uuid not null references plants(id) on delete cascade,
    indication_id uuid not null references indications(id) on delete cascade,
    preparation_id uuid references preparations(id) on delete set null,
    source_id uuid not null references sources(id) on delete restrict,
    evidence_domain text not null
        check (evidence_domain in ('regulatory','traditional','clinical','preclinical','other')),
    evidence_type text,
    study_design text,
    population text,
    sample_size integer check (sample_size is null or sample_size >= 0),
    outcome_direction text
        check (outcome_direction is null or outcome_direction in ('supportive','mixed','negative','neutral','unknown')),
    quality_label text
        check (quality_label is null or quality_label in ('high','moderate','low','unclear')),
    indication_match numeric
        check (indication_match is null or indication_match between 0 and 1),
    summary text,
    ai_extracted boolean not null default false,
    extraction_model text,
    extraction_confidence numeric
        check (extraction_confidence is null or extraction_confidence between 0 and 1),
    human_verified boolean not null default false,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists safety_records (
    id uuid primary key default gen_random_uuid(),
    plant_id uuid not null references plants(id) on delete cascade,
    preparation_id uuid references preparations(id) on delete set null,
    source_id uuid not null references sources(id) on delete restrict,
    contraindications text[] not null default '{}',
    precautions text[] not null default '{}',
    interactions text[] not null default '{}',
    adverse_effects text[] not null default '{}',
    age_restrictions text[] not null default '{}',
    pregnancy_lactation text,
    toxicity text,
    ai_extracted boolean not null default false,
    human_verified boolean not null default false,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists constituent_indication_evidence (
    id uuid primary key default gen_random_uuid(),
    constituent_id uuid not null references constituents(id) on delete cascade,
    indication_id uuid not null references indications(id) on delete cascade,
    plant_id uuid references plants(id) on delete set null,
    source_id uuid not null references sources(id) on delete restrict,
    evidence_domain text not null
        check (evidence_domain in ('clinical','preclinical','mechanistic','other')),
    study_design text,
    model_system text,
    population text,
    sample_size integer check (sample_size is null or sample_size >= 0),
    outcome_direction text
        check (outcome_direction is null or outcome_direction in ('supportive','mixed','negative','neutral','unknown')),
    quality_label text
        check (quality_label is null or quality_label in ('high','moderate','low','unclear')),
    indication_match numeric
        check (indication_match is null or indication_match between 0 and 1),
    summary text,
    ai_extracted boolean not null default false,
    extraction_model text,
    extraction_confidence numeric
        check (extraction_confidence is null or extraction_confidence between 0 and 1),
    human_verified boolean not null default false,
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists extraction_runs (
    id uuid primary key default gen_random_uuid(),
    plant_id uuid not null references plants(id) on delete cascade,
    indication_id uuid references indications(id) on delete set null,
    source_id uuid not null references sources(id) on delete restrict,
    pipeline text not null,
    schema_version text not null,
    validation_status text not null
        check (validation_status in ('pass','warning','fail')),
    model_provider text,
    model_name text,
    prompt_version text,
    profile_json jsonb not null,
    validation_summary jsonb not null default '{}'::jsonb,
    human_review_status text not null default 'pending'
        check (human_review_status in ('pending','accepted','rejected')),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists mapping_runs (
    id uuid primary key default gen_random_uuid(),
    plant_id uuid not null references plants(id) on delete cascade,
    ema_run_id uuid not null references extraction_runs(id) on delete restrict,
    tcm_run_id uuid not null references extraction_runs(id) on delete restrict,
    mapping_version text not null,
    validation_status text not null
        check (validation_status in ('pass','warning','fail')),
    model_provider text,
    model_name text,
    prompt_version text,
    profile_json jsonb not null,
    validation_summary jsonb not null default '{}'::jsonb,
    human_review_status text not null default 'pending'
        check (human_review_status in ('pending','accepted','rejected')),
    metadata jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now()
);

create table if not exists plant_indication_profiles (
    id uuid primary key default gen_random_uuid(),
    plant_id uuid not null references plants(id) on delete cascade,
    indication_id uuid not null references indications(id) on delete cascade,
    preparation_id uuid references preparations(id) on delete set null,
    evidence_category text not null default 'unclassified'
        check (evidence_category in ('established','traditional','emerging','evidence_gap','unclassified')),
    evidence_relevance_score numeric
        check (evidence_relevance_score is null or evidence_relevance_score between 0 and 1),
    traditional_support_score numeric
        check (traditional_support_score is null or traditional_support_score between 0 and 1),
    modern_evidence_score numeric
        check (modern_evidence_score is null or modern_evidence_score between 0 and 1),
    source_convergence_score numeric
        check (source_convergence_score is null or source_convergence_score between 0 and 1),
    research_opportunity text not null default 'unclassified'
        check (research_opportunity in ('high','moderate','low','none','unclassified')),
    profile_rationale text,
    scoring_version text,
    last_scored_at timestamptz,
    created_at timestamptz not null default now()
);

create table if not exists plant_ingestion_queue (
    id uuid primary key default gen_random_uuid(),
    scientific_name text not null,
    target_indication text,
    plant_id uuid references plants(id) on delete set null,
    ema_source_url text,
    traditional_source_url text,
    traditional_system text,
    source_discovery_mode text not null default 'assisted'
        check (source_discovery_mode in ('manual','assisted','auto')),
    modules jsonb not null default '{
        "ema": true,
        "safety": true,
        "mapping": true,
        "scoring": true,
        "traditional": true,
        "constituents": true,
        "modern_evidence": true
    }'::jsonb,
    priority integer not null default 100 check (priority >= 0),
    status text not null default 'pending'
        check (status in ('pending','running','review_required','completed','failed','paused')),
    current_step text,
    attempts integer not null default 0 check (attempts >= 0),
    last_error text,
    metadata jsonb not null default '{}'::jsonb,
    started_at timestamptz,
    completed_at timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    indication_context text
);

create index if not exists idx_extraction_runs_plant_created
    on extraction_runs (plant_id, created_at desc);

create index if not exists idx_mapping_runs_plant_created
    on mapping_runs (plant_id, created_at desc);

create index if not exists idx_profiles_indication_score
    on plant_indication_profiles (indication_id, evidence_relevance_score desc);

create index if not exists idx_queue_status_priority
    on plant_ingestion_queue (status, priority, created_at);
