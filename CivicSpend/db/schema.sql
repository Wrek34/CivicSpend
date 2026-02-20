-- CivicSpend Database Schema

CREATE TABLE IF NOT EXISTS run_manifest (
    run_id TEXT PRIMARY KEY,
    run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    filters_json TEXT,
    row_count_raw INTEGER,
    status TEXT
);

CREATE TABLE IF NOT EXISTS raw_awards (
    run_id TEXT NOT NULL,
    award_id TEXT NOT NULL,
    recipient_name TEXT,
    recipient_duns TEXT,
    awarding_agency_name TEXT,
    action_date DATE,
    obligation_amount DECIMAL(18,2),
    place_of_performance_state TEXT,
    PRIMARY KEY (run_id, award_id)
);

CREATE INDEX IF NOT EXISTS idx_raw_awards_run_id ON raw_awards(run_id);
