
-- GPAT AI Learning System
-- Supabase/PostgreSQL V0 production baseline
-- Frozen architecture: PostgreSQL + pgvector + Supabase Auth/RLS.
-- Files live outside Postgres (R2); this schema stores metadata and object keys.
-- Embeddings: V0 uses text-embedding-3-small with 1536 dimensions.
-- Apply through Supabase migrations, not ad-hoc production SQL.

begin;

create extension if not exists pgcrypto;
create extension if not exists vector;

create schema if not exists app;

-- ============================================================
-- ENUMS
-- ============================================================

do $$ begin
  create type app.source_kind as enum (
    'official',
    'primary_academic',
    'textbook',
    'secondary_educational',
    'user_material',
    'ai_generated'
  );
exception when duplicate_object then null; end $$;

do $$ begin
  create type app.record_status as enum (
    'draft',
    'active',
    'deprecated',
    'rejected'
  );
exception when duplicate_object then null; end $$;

do $$ begin
  create type app.processing_status as enum (
    'queued',
    'processing',
    'completed',
    'failed'
  );
exception when duplicate_object then null; end $$;

do $$ begin
  create type app.verification_status as enum (
    'unverified',
    'ai_checked',
    'human_verified',
    'rejected',
    'conflict'
  );
exception when duplicate_object then null; end $$;

do $$ begin
  create type app.block_type as enum (
    'document_title',
    'heading',
    'subheading',
    'paragraph',
    'list',
    'table',
    'figure',
    'formula',
    'caption',
    'question',
    'answer',
    'note',
    'warning'
  );
exception when duplicate_object then null; end $$;

do $$ begin
  create type app.relationship_type as enum (
    'prerequisite_of',
    'related_to',
    'part_of',
    'causes',
    'treats',
    'inhibits',
    'activates',
    'antagonizes',
    'agonizes',
    'contrasts_with',
    'confused_with',
    'example_of',
    'derived_from'
  );
exception when duplicate_object then null; end $$;

do $$ begin
  create type app.question_type as enum (
    'mcq',
    'true_false',
    'short_recall',
    'fill_blank',
    'image_identification',
    'numerical',
    'clinical_scenario',
    'conceptual',
    'comparison',
    'mechanism',
    'reverse_recall'
  );
exception when duplicate_object then null; end $$;

do $$ begin
  create type app.question_origin as enum (
    'human',
    'pyq',
    'ai_generated',
    'imported'
  );
exception when duplicate_object then null; end $$;

do $$ begin
  create type app.error_type as enum (
    'factual_gap',
    'concept_confusion',
    'terminology',
    'calculation',
    'question_interpretation',
    'careless_error',
    'overconfidence'
  );
exception when duplicate_object then null; end $$;

do $$ begin
  create type app.session_type as enum (
    'daily_review',
    'new_learning',
    'weakness_repair',
    'mock_test',
    'pyq',
    'quick_recall'
  );
exception when duplicate_object then null; end $$;

-- ============================================================
-- COMMON UPDATED_AT TRIGGER
-- ============================================================

create or replace function app.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- ============================================================
-- USER PROFILE
-- auth.users is owned by Supabase Auth.
-- Never expose auth.users directly.
-- ============================================================

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  avatar_url text,
  exam_id uuid,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- ============================================================
-- EXAM / SYLLABUS VERSIONING
-- Never hard-code GPAT 2027 assumptions.
-- ============================================================

create table if not exists public.exams (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  name text not null,
  authority text,
  created_at timestamptz not null default now(),
  check (length(trim(code)) > 0)
);

create table if not exists public.sources (
  id uuid primary key default gen_random_uuid(),
  owner_user_id uuid references auth.users(id) on delete cascade,
  title text not null,
  source_kind app.source_kind not null,
  author text,
  publisher text,
  edition text,
  publication_year integer,
  url text,
  license text,
  authority_level smallint not null check (authority_level between 0 and 5),
  checksum_sha256 text,
  status app.record_status not null default 'active',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.syllabus_versions (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  name text not null,
  authority text,
  source_id uuid references public.sources(id) on delete set null,
  effective_from date,
  effective_to date,
  is_authoritative boolean not null default false,
  status app.record_status not null default 'active',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (effective_to is null or effective_from is null or effective_to >= effective_from)
);

create table if not exists public.exam_versions (
  id uuid primary key default gen_random_uuid(),
  exam_id uuid not null references public.exams(id) on delete cascade,
  code text not null unique,
  name text not null,
  syllabus_version_id uuid references public.syllabus_versions(id) on delete set null,
  official_bulletin_source_id uuid references public.sources(id) on delete set null,
  is_authoritative boolean not null default false,
  status app.record_status not null default 'active',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.exam_blueprints (
  id uuid primary key default gen_random_uuid(),
  exam_version_id uuid not null references public.exam_versions(id) on delete cascade,
  subject_id uuid,
  question_count integer check (question_count is null or question_count > 0),
  total_marks numeric check (total_marks is null or total_marks >= 0),
  duration_minutes integer check (duration_minutes is null or duration_minutes > 0),
  marking_correct numeric,
  marking_incorrect numeric,
  marking_unattempted numeric default 0,
  timing_rules jsonb not null default '{}'::jsonb,
  source_id uuid references public.sources(id) on delete set null,
  is_authoritative boolean not null default false,
  created_at timestamptz not null default now()
);

create table if not exists public.subjects (
  id uuid primary key default gen_random_uuid(),
  syllabus_version_id uuid not null references public.syllabus_versions(id) on delete cascade,
  code text not null,
  name text not null,
  description text,
  exam_weight numeric,
  importance_score numeric not null default 0.5 check (importance_score between 0 and 1),
  status app.record_status not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (syllabus_version_id, code)
);

alter table public.exam_blueprints
  add constraint exam_blueprints_subject_fk
  foreign key (subject_id) references public.subjects(id) on delete set null;

create table if not exists public.topics (
  id uuid primary key default gen_random_uuid(),
  subject_id uuid not null references public.subjects(id) on delete cascade,
  parent_topic_id uuid references public.topics(id) on delete set null,
  code text,
  name text not null,
  description text,
  importance_score numeric not null default 0.5 check (importance_score between 0 and 1),
  status app.record_status not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (subject_id, name)
);

create table if not exists public.concepts (
  id uuid primary key default gen_random_uuid(),
  topic_id uuid not null references public.topics(id) on delete cascade,
  canonical_name text not null,
  canonical_definition text,
  learning_objective text,
  difficulty numeric check (difficulty is null or difficulty between 0 and 1),
  importance_score numeric not null default 0.5 check (importance_score between 0 and 1),
  status app.record_status not null default 'active',
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (topic_id, canonical_name)
);

create table if not exists public.concept_relationships (
  id uuid primary key default gen_random_uuid(),
  source_concept_id uuid not null references public.concepts(id) on delete cascade,
  target_concept_id uuid not null references public.concepts(id) on delete cascade,
  relationship_type app.relationship_type not null,
  confidence numeric not null default 1.0 check (confidence between 0 and 1),
  source_id uuid references public.sources(id) on delete set null,
  created_at timestamptz not null default now(),
  unique (source_concept_id, target_concept_id, relationship_type),
  check (source_concept_id <> target_concept_id)
);

-- ============================================================
-- DOCUMENT INGESTION
-- Files are stored in R2; only object keys/metadata live here.
-- ============================================================

create table if not exists public.documents (
  id uuid primary key default gen_random_uuid(),
  owner_user_id uuid references auth.users(id) on delete cascade,
  source_id uuid not null references public.sources(id) on delete cascade,
  filename text not null,
  mime_type text not null,
  storage_provider text not null default 'r2',
  storage_bucket text,
  storage_key text not null,
  file_size_bytes bigint check (file_size_bytes is null or file_size_bytes >= 0),
  page_count integer check (page_count is null or page_count >= 0),
  language text,
  checksum_sha256 text,
  processing_status app.processing_status not null default 'queued',
  processing_error text,
  parser_name text,
  parser_version text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (storage_provider, storage_bucket, storage_key)
);

create table if not exists public.document_pages (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references public.documents(id) on delete cascade,
  page_number integer not null check (page_number > 0),
  raw_text text,
  image_storage_key text,
  layout_json jsonb not null default '{}'::jsonb,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (document_id, page_number)
);

create table if not exists public.content_blocks (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references public.documents(id) on delete cascade,
  page_id uuid not null references public.document_pages(id) on delete cascade,
  parent_block_id uuid references public.content_blocks(id) on delete set null,
  block_type app.block_type not null,
  heading text,
  content text not null,
  reading_order integer,
  bbox jsonb,
  topic_id uuid references public.topics(id) on delete set null,
  concept_id uuid references public.concepts(id) on delete set null,
  token_count integer check (token_count is null or token_count >= 0),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.knowledge_images (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references public.documents(id) on delete cascade,
  page_id uuid not null references public.document_pages(id) on delete cascade,
  content_block_id uuid references public.content_blocks(id) on delete set null,
  storage_key text not null,
  image_type text,
  ocr_text text,
  vlm_description text,
  concept_id uuid references public.concepts(id) on delete set null,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

-- ============================================================
-- CLAIM / EVIDENCE LAYER
-- ============================================================

create table if not exists public.claims (
  id uuid primary key default gen_random_uuid(),
  concept_id uuid references public.concepts(id) on delete set null,
  source_block_id uuid references public.content_blocks(id) on delete set null,
  claim_text text not null,
  confidence numeric check (confidence is null or confidence between 0 and 1),
  verification_status app.verification_status not null default 'unverified',
  verified_by uuid references auth.users(id) on delete set null,
  verified_at timestamptz,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.claim_sources (
  claim_id uuid not null references public.claims(id) on delete cascade,
  source_id uuid not null references public.sources(id) on delete cascade,
  page_id uuid references public.document_pages(id) on delete set null,
  support_type text not null default 'direct',
  PRIMARY KEY (claim_id, source_id)
);

-- ============================================================
-- EMBEDDINGS
-- V0: text-embedding-3-small / 1536 dimensions.
-- Keep the model in metadata so migration is explicit if changed.
-- ============================================================

create table if not exists public.content_block_embeddings (
  content_block_id uuid primary key references public.content_blocks(id) on delete cascade,
  model text not null default 'text-embedding-3-small',
  dimensions integer not null default 1536 check (dimensions = 1536),
  embedding vector(1536) not null,
  created_at timestamptz not null default now()
);

-- ============================================================
-- QUESTIONS
-- ============================================================

create table if not exists public.questions (
  id uuid primary key default gen_random_uuid(),
  owner_user_id uuid references auth.users(id) on delete cascade,
  concept_id uuid references public.concepts(id) on delete set null,
  question_type app.question_type not null,
  origin app.question_origin not null,
  question_text text not null,
  difficulty numeric check (difficulty is null or difficulty between 0 and 1),
  correct_answer text,
  explanation text,
  hint text,
  verification_status app.verification_status not null default 'unverified',
  quality_score numeric check (quality_score is null or quality_score between 0 and 1),
  generated_by text,
  generated_model text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.question_options (
  id uuid primary key default gen_random_uuid(),
  question_id uuid not null references public.questions(id) on delete cascade,
  option_key text not null,
  option_text text not null,
  is_correct boolean not null default false,
  distractor_reason text,
  sort_order integer not null default 0,
  unique (question_id, option_key)
);

create unique index if not exists one_correct_option_per_question
  on public.question_options(question_id)
  where is_correct = true;

create table if not exists public.question_sources (
  question_id uuid not null references public.questions(id) on delete cascade,
  source_id uuid not null references public.sources(id) on delete cascade,
  page_id uuid references public.document_pages(id) on delete set null,
  relationship text not null default 'directly_supported',
  PRIMARY KEY (question_id, source_id)
);

-- ============================================================
-- AI / RETRIEVAL OBSERVABILITY
-- ============================================================

create table if not exists public.ai_runs (
  id uuid primary key default gen_random_uuid(),
  owner_user_id uuid references auth.users(id) on delete cascade,
  run_type text not null,
  provider text,
  model text,
  request_id text,
  input_tokens integer,
  output_tokens integer,
  latency_ms integer,
  status text not null default 'completed',
  error_message text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.retrieval_runs (
  id uuid primary key default gen_random_uuid(),
  owner_user_id uuid references auth.users(id) on delete cascade,
  query_text text not null,
  embedding_model text,
  top_k integer not null default 10 check (top_k > 0),
  reranker text,
  latency_ms integer,
  created_at timestamptz not null default now()
);

create table if not exists public.retrieval_results (
  id uuid primary key default gen_random_uuid(),
  retrieval_run_id uuid not null references public.retrieval_runs(id) on delete cascade,
  content_block_id uuid not null references public.content_blocks(id) on delete cascade,
  retrieval_method text not null,
  rank_position integer not null check (rank_position > 0),
  score numeric,
  rerank_score numeric,
  created_at timestamptz not null default now(),
  unique (retrieval_run_id, content_block_id)
);

create table if not exists public.answer_runs (
  id uuid primary key default gen_random_uuid(),
  owner_user_id uuid references auth.users(id) on delete cascade,
  question_text text not null,
  answer_text text,
  retrieval_run_id uuid references public.retrieval_runs(id) on delete set null,
  ai_run_id uuid references public.ai_runs(id) on delete set null,
  verification_status app.verification_status not null default 'unverified',
  confidence numeric check (confidence is null or confidence between 0 and 1),
  unsupported_claim_count integer not null default 0 check (unsupported_claim_count >= 0),
  created_at timestamptz not null default now()
);

create table if not exists public.answer_claims (
  id uuid primary key default gen_random_uuid(),
  answer_run_id uuid not null references public.answer_runs(id) on delete cascade,
  claim_text text not null,
  support_status text not null,
  supporting_claim_id uuid references public.claims(id) on delete set null,
  created_at timestamptz not null default now()
);

-- ============================================================
-- LEARNER MODEL
-- ============================================================

create table if not exists public.attempts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  question_id uuid not null references public.questions(id) on delete cascade,
  started_at timestamptz,
  answered_at timestamptz not null default now(),
  selected_answer text,
  correct boolean not null,
  response_time_ms integer check (response_time_ms is null or response_time_ms >= 0),
  confidence smallint check (confidence is null or confidence between 1 and 5),
  hint_used boolean not null default false,
  explanation_viewed boolean not null default false,
  answer_run_id uuid references public.answer_runs(id) on delete set null,
  metadata jsonb not null default '{}'::jsonb
);

create table if not exists public.review_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  concept_id uuid not null references public.concepts(id) on delete cascade,
  question_id uuid references public.questions(id) on delete set null,
  attempt_id uuid references public.attempts(id) on delete set null,

  rating smallint not null check (rating between 1 and 4),
  response_time_ms integer check (response_time_ms is null or response_time_ms >= 0),
  confidence smallint check (confidence is null or confidence between 1 and 5),

  reviewed_at timestamptz not null default now(),

  pre_stability numeric,
  post_stability numeric,
  pre_retrievability numeric,
  post_retrievability numeric,
  pre_difficulty numeric,
  post_difficulty numeric,

  scheduled_for timestamptz,
  metadata jsonb not null default '{}'::jsonb
);

create table if not exists public.concept_mastery (
  user_id uuid not null references auth.users(id) on delete cascade,
  concept_id uuid not null references public.concepts(id) on delete cascade,

  mastery_score numeric not null default 0 check (mastery_score between 0 and 1),
  difficulty numeric,
  stability numeric,
  retrievability numeric,

  attempt_count integer not null default 0 check (attempt_count >= 0),
  correct_count integer not null default 0 check (correct_count >= 0),

  confidence_calibration numeric,
  misconception_risk numeric check (misconception_risk is null or misconception_risk between 0 and 1),

  last_reviewed timestamptz,
  next_review timestamptz,

  updated_at timestamptz not null default now(),

  primary key (user_id, concept_id),
  check (correct_count <= attempt_count)
);

create table if not exists public.misconceptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  concept_id uuid not null references public.concepts(id) on delete cascade,
  type app.error_type not null,
  description text not null,
  confidence numeric check (confidence is null or confidence between 0 and 1),
  first_detected timestamptz not null default now(),
  last_detected timestamptz not null default now(),
  resolved boolean not null default false,
  resolved_at timestamptz,
  metadata jsonb not null default '{}'::jsonb
);

-- ============================================================
-- STUDY SESSIONS
-- ============================================================

create table if not exists public.study_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  session_type app.session_type not null,
  started_at timestamptz,
  ended_at timestamptz,
  planned_duration_minutes integer check (planned_duration_minutes is null or planned_duration_minutes > 0),
  actual_duration_minutes integer check (actual_duration_minutes is null or actual_duration_minutes >= 0),
  completion_score numeric check (completion_score is null or completion_score between 0 and 1),
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.study_session_items (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.study_sessions(id) on delete cascade,
  concept_id uuid references public.concepts(id) on delete set null,
  question_id uuid references public.questions(id) on delete set null,
  item_type text not null,
  sequence integer not null check (sequence > 0),
  completed boolean not null default false,
  completed_at timestamptz,
  metadata jsonb not null default '{}'::jsonb,
  unique (session_id, sequence)
);

-- ============================================================
-- INDEXES
-- ============================================================

create index if not exists idx_sources_owner
  on public.sources(owner_user_id);

create index if not exists idx_sources_authority
  on public.sources(authority_level);

create index if not exists idx_documents_owner
  on public.documents(owner_user_id);

create index if not exists idx_documents_source
  on public.documents(source_id);

create index if not exists idx_documents_processing
  on public.documents(processing_status);

create index if not exists idx_document_pages_document
  on public.document_pages(document_id, page_number);

create index if not exists idx_content_blocks_document
  on public.content_blocks(document_id, page_id, reading_order);

create index if not exists idx_content_blocks_concept
  on public.content_blocks(concept_id);

create index if not exists idx_content_blocks_topic
  on public.content_blocks(topic_id);

create index if not exists idx_content_blocks_fts
  on public.content_blocks using gin (to_tsvector('english', content));

create index if not exists idx_claims_concept
  on public.claims(concept_id);

create index if not exists idx_claims_verification
  on public.claims(verification_status);

create index if not exists idx_concept_relationships_source
  on public.concept_relationships(source_concept_id);

create index if not exists idx_concept_relationships_target
  on public.concept_relationships(target_concept_id);

create index if not exists idx_questions_concept
  on public.questions(concept_id);

create index if not exists idx_questions_verification
  on public.questions(verification_status);

create index if not exists idx_questions_origin
  on public.questions(origin);

create index if not exists idx_attempts_user_time
  on public.attempts(user_id, answered_at desc);

create index if not exists idx_attempts_question
  on public.attempts(question_id);

create index if not exists idx_review_logs_user_next
  on public.review_logs(user_id, scheduled_for);

create index if not exists idx_review_logs_concept_time
  on public.review_logs(concept_id, reviewed_at desc);

create index if not exists idx_mastery_user_next
  on public.concept_mastery(user_id, next_review);

create index if not exists idx_mastery_user_score
  on public.concept_mastery(user_id, mastery_score);

create index if not exists idx_misconceptions_user_active
  on public.misconceptions(user_id, resolved, last_detected desc);

create index if not exists idx_sessions_user_time
  on public.study_sessions(user_id, created_at desc);

create index if not exists idx_retrieval_results_run_rank
  on public.retrieval_results(retrieval_run_id, rank_position);

create index if not exists idx_answer_runs_user_time
  on public.answer_runs(owner_user_id, created_at desc);

-- HNSW index for semantic search.
-- Tune lists/ef_search later from measured retrieval performance.
create index if not exists idx_content_block_embeddings_hnsw
  on public.content_block_embeddings
  using hnsw (embedding vector_cosine_ops);

-- ============================================================
-- UPDATED_AT TRIGGERS
-- ============================================================

drop trigger if exists profiles_set_updated_at on public.profiles;
create trigger profiles_set_updated_at
before update on public.profiles
for each row execute function app.set_updated_at();

drop trigger if exists sources_set_updated_at on public.sources;
create trigger sources_set_updated_at
before update on public.sources
for each row execute function app.set_updated_at();

drop trigger if exists syllabus_versions_set_updated_at on public.syllabus_versions;
create trigger syllabus_versions_set_updated_at
before update on public.syllabus_versions
for each row execute function app.set_updated_at();

drop trigger if exists exam_versions_set_updated_at on public.exam_versions;
create trigger exam_versions_set_updated_at
before update on public.exam_versions
for each row execute function app.set_updated_at();

drop trigger if exists subjects_set_updated_at on public.subjects;
create trigger subjects_set_updated_at
before update on public.subjects
for each row execute function app.set_updated_at();

drop trigger if exists topics_set_updated_at on public.topics;
create trigger topics_set_updated_at
before update on public.topics
for each row execute function app.set_updated_at();

drop trigger if exists concepts_set_updated_at on public.concepts;
create trigger concepts_set_updated_at
before update on public.concepts
for each row execute function app.set_updated_at();

drop trigger if exists documents_set_updated_at on public.documents;
create trigger documents_set_updated_at
before update on public.documents
for each row execute function app.set_updated_at();

drop trigger if exists claims_set_updated_at on public.claims;
create trigger claims_set_updated_at
before update on public.claims
for each row execute function app.set_updated_at();

drop trigger if exists questions_set_updated_at on public.questions;
create trigger questions_set_updated_at
before update on public.questions
for each row execute function app.set_updated_at();

drop trigger if exists concept_mastery_set_updated_at on public.concept_mastery;
create trigger concept_mastery_set_updated_at
before update on public.concept_mastery
for each row execute function app.set_updated_at();

-- ============================================================
-- PROFILE CREATION FROM SUPABASE AUTH
-- ============================================================

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, display_name)
  values (
    new.id,
    coalesce(new.raw_user_meta_data ->> 'full_name',
             new.raw_user_meta_data ->> 'name')
  )
  on conflict (id) do nothing;

  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.handle_new_user();

-- ============================================================
-- RLS
-- ============================================================

alter table public.profiles enable row level security;
alter table public.exams enable row level security;
alter table public.sources enable row level security;
alter table public.syllabus_versions enable row level security;
alter table public.exam_versions enable row level security;
alter table public.exam_blueprints enable row level security;
alter table public.subjects enable row level security;
alter table public.topics enable row level security;
alter table public.concepts enable row level security;
alter table public.concept_relationships enable row level security;
alter table public.documents enable row level security;
alter table public.document_pages enable row level security;
alter table public.content_blocks enable row level security;
alter table public.knowledge_images enable row level security;
alter table public.claims enable row level security;
alter table public.claim_sources enable row level security;
alter table public.content_block_embeddings enable row level security;
alter table public.questions enable row level security;
alter table public.question_options enable row level security;
alter table public.question_sources enable row level security;
alter table public.ai_runs enable row level security;
alter table public.retrieval_runs enable row level security;
alter table public.retrieval_results enable row level security;
alter table public.answer_runs enable row level security;
alter table public.answer_claims enable row level security;
alter table public.attempts enable row level security;
alter table public.review_logs enable row level security;
alter table public.concept_mastery enable row level security;
alter table public.misconceptions enable row level security;
alter table public.study_sessions enable row level security;
alter table public.study_session_items enable row level security;

-- Helper: source is public/system or owned by current user.
create or replace function app.can_read_source(p_source_id uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.sources s
    where s.id = p_source_id
      and (s.owner_user_id is null or s.owner_user_id = auth.uid())
  );
$$;

-- Helper: document is system-owned or owned by current user.
create or replace function app.can_read_document(p_document_id uuid)
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.documents d
    where d.id = p_document_id
      and (d.owner_user_id is null or d.owner_user_id = auth.uid())
  );
$$;

-- Profiles
create policy profiles_select_own on public.profiles
for select to authenticated
using (id = auth.uid());

create policy profiles_update_own on public.profiles
for update to authenticated
using (id = auth.uid())
with check (id = auth.uid());

-- Exams / syllabus / ontology are authenticated-read.
create policy exams_read on public.exams
for select to authenticated using (true);

create policy syllabus_read on public.syllabus_versions
for select to authenticated using (true);

create policy exam_versions_read on public.exam_versions
for select to authenticated using (true);

create policy blueprints_read on public.exam_blueprints
for select to authenticated using (true);

create policy subjects_read on public.subjects
for select to authenticated using (true);

create policy topics_read on public.topics
for select to authenticated using (true);

create policy concepts_read on public.concepts
for select to authenticated using (true);

create policy relationships_read on public.concept_relationships
for select to authenticated using (true);

-- Sources
create policy sources_read on public.sources
for select to authenticated
using (owner_user_id is null or owner_user_id = auth.uid());

create policy sources_insert_own on public.sources
for insert to authenticated
with check (owner_user_id = auth.uid());

create policy sources_update_own on public.sources
for update to authenticated
using (owner_user_id = auth.uid())
with check (owner_user_id = auth.uid());

create policy sources_delete_own on public.sources
for delete to authenticated
using (owner_user_id = auth.uid());

-- Documents
create policy documents_read on public.documents
for select to authenticated
using (owner_user_id is null or owner_user_id = auth.uid());

create policy documents_insert_own on public.documents
for insert to authenticated
with check (owner_user_id = auth.uid());

create policy documents_update_own on public.documents
for update to authenticated
using (owner_user_id = auth.uid())
with check (owner_user_id = auth.uid());

create policy documents_delete_own on public.documents
for delete to authenticated
using (owner_user_id = auth.uid());

-- Document-derived data: readable if parent document is readable.
create policy pages_read on public.document_pages
for select to authenticated
using (app.can_read_document(document_id));

create policy blocks_read on public.content_blocks
for select to authenticated
using (app.can_read_document(document_id));

create policy images_read on public.knowledge_images
for select to authenticated
using (app.can_read_document(document_id));

create policy embeddings_read on public.content_block_embeddings
for select to authenticated
using (exists (
  select 1 from public.content_blocks cb
  where cb.id = content_block_id
    and app.can_read_document(cb.document_id)
));

create policy claims_read on public.claims
for select to authenticated
using (
  source_block_id is null
  or exists (
    select 1
    from public.content_blocks cb
    where cb.id = source_block_id
      and app.can_read_document(cb.document_id)
  )
);

create policy claim_sources_read on public.claim_sources
for select to authenticated
using (
  app.can_read_source(source_id)
);

-- Questions / options / sources
create policy questions_read on public.questions
for select to authenticated
using (owner_user_id is null or owner_user_id = auth.uid());

create policy questions_insert_own on public.questions
for insert to authenticated
with check (owner_user_id = auth.uid());

create policy questions_update_own on public.questions
for update to authenticated
using (owner_user_id = auth.uid())
with check (owner_user_id = auth.uid());

create policy questions_delete_own on public.questions
for delete to authenticated
using (owner_user_id = auth.uid());

create policy question_options_read on public.question_options
for select to authenticated
using (exists (
  select 1 from public.questions q
  where q.id = question_id
    and (q.owner_user_id is null or q.owner_user_id = auth.uid())
));

create policy question_sources_read on public.question_sources
for select to authenticated
using (app.can_read_source(source_id));

-- AI/retrieval/answer observability is private to the user.
create policy ai_runs_own on public.ai_runs
for all to authenticated
using (owner_user_id = auth.uid())
with check (owner_user_id = auth.uid());

create policy retrieval_runs_own on public.retrieval_runs
for all to authenticated
using (owner_user_id = auth.uid())
with check (owner_user_id = auth.uid());

create policy retrieval_results_read_own on public.retrieval_results
for select to authenticated
using (exists (
  select 1 from public.retrieval_runs rr
  where rr.id = retrieval_run_id
    and rr.owner_user_id = auth.uid()
));

create policy answer_runs_own on public.answer_runs
for all to authenticated
using (owner_user_id = auth.uid())
with check (owner_user_id = auth.uid());

create policy answer_claims_read_own on public.answer_claims
for select to authenticated
using (exists (
  select 1 from public.answer_runs ar
  where ar.id = answer_run_id
    and ar.owner_user_id = auth.uid()
));

-- Learner data
create policy attempts_own on public.attempts
for all to authenticated
using (user_id = auth.uid())
with check (user_id = auth.uid());

create policy review_logs_own on public.review_logs
for all to authenticated
using (user_id = auth.uid())
with check (user_id = auth.uid());

create policy mastery_own on public.concept_mastery
for all to authenticated
using (user_id = auth.uid())
with check (user_id = auth.uid());

create policy misconceptions_own on public.misconceptions
for all to authenticated
using (user_id = auth.uid())
with check (user_id = auth.uid());

create policy sessions_own on public.study_sessions
for all to authenticated
using (user_id = auth.uid())
with check (user_id = auth.uid());

create policy session_items_own on public.study_session_items
for all to authenticated
using (exists (
  select 1 from public.study_sessions ss
  where ss.id = session_id
    and ss.user_id = auth.uid()
));

-- ============================================================
-- DEFAULT PRIVILEGES
-- Keep public API access constrained; service_role bypasses RLS.
-- ============================================================

revoke all on all tables in schema public from anon;
revoke all on all tables in schema public from authenticated;

grant select on
  public.exams,
  public.syllabus_versions,
  public.exam_versions,
  public.exam_blueprints,
  public.subjects,
  public.topics,
  public.concepts,
  public.concept_relationships,
  public.sources,
  public.documents,
  public.document_pages,
  public.content_blocks,
  public.knowledge_images,
  public.claims,
  public.claim_sources,
  public.content_block_embeddings,
  public.questions,
  public.question_options,
  public.question_sources,
  public.retrieval_results,
  public.answer_claims
to authenticated;

grant select, update on public.profiles to authenticated;

grant select, insert, update, delete on
  public.sources,
  public.documents,
  public.questions,
  public.ai_runs,
  public.retrieval_runs,
  public.answer_runs,
  public.attempts,
  public.review_logs,
  public.concept_mastery,
  public.misconceptions,
  public.study_sessions,
  public.study_session_items
to authenticated;

-- Child tables that users can safely insert/update through the app.
grant insert, update, delete on
  public.question_options
to authenticated;

-- Sequence/identity permissions are intentionally absent because this schema
-- uses UUIDs rather than serial/identity keys.

commit;
