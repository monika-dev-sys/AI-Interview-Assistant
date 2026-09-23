-- database/schema.sql
-- SQLite schema for AI Interview Assistant

CREATE TABLE IF NOT EXISTS candidates (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL DEFAULT '',
    email       TEXT,
    data_json   TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sessions (
    id              TEXT PRIMARY KEY,
    candidate_id    TEXT NOT NULL,
    interview_type  TEXT NOT NULL,
    difficulty      TEXT NOT NULL,
    target_role     TEXT NOT NULL DEFAULT '',
    started_at      TEXT NOT NULL,
    ended_at        TEXT,
    is_complete     INTEGER NOT NULL DEFAULT 0,
    data_json       TEXT NOT NULL,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

CREATE INDEX IF NOT EXISTS idx_sessions_candidate ON sessions(candidate_id);
CREATE INDEX IF NOT EXISTS idx_sessions_started   ON sessions(started_at DESC);

CREATE TABLE IF NOT EXISTS scores (
    session_id      TEXT PRIMARY KEY,
    candidate_id    TEXT NOT NULL,
    overall_score   REAL NOT NULL DEFAULT 0,
    data_json       TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (session_id)   REFERENCES sessions(id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

CREATE TABLE IF NOT EXISTS feedback (
    session_id      TEXT PRIMARY KEY,
    candidate_id    TEXT NOT NULL,
    data_json       TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (session_id)   REFERENCES sessions(id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

-- ============================================================
-- Recruitment / Resume Screening
-- ============================================================

CREATE TABLE IF NOT EXISTS jobs (
    id              TEXT PRIMARY KEY,
    role            TEXT NOT NULL,
    required_skills TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS screening_results (
    id                TEXT PRIMARY KEY,
    job_id            TEXT NOT NULL,
    candidate_id      TEXT NOT NULL,

    skill_score       REAL NOT NULL DEFAULT 0,
    semantic_score    REAL NOT NULL DEFAULT 0,
    experience_score  REAL NOT NULL DEFAULT 0,
    project_score     REAL NOT NULL DEFAULT 0,
    education_score   REAL NOT NULL DEFAULT 0,

    final_score       REAL NOT NULL DEFAULT 0,
    rank              INTEGER,

    matched_skills    TEXT NOT NULL DEFAULT '[]',
    missing_skills    TEXT NOT NULL DEFAULT '[]',

    status            TEXT NOT NULL DEFAULT 'SCREENED',

    created_at        TEXT NOT NULL DEFAULT (datetime('now')),

    FOREIGN KEY (job_id) REFERENCES jobs(id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

CREATE INDEX IF NOT EXISTS idx_screening_job
    ON screening_results(job_id);

CREATE INDEX IF NOT EXISTS idx_screening_candidate
    ON screening_results(candidate_id);

CREATE INDEX IF NOT EXISTS idx_screening_score
    ON screening_results(final_score DESC);