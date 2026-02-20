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

CREATE TABLE IF NOT EXISTS vendor_entities (
    vendor_id TEXT PRIMARY KEY,
    canonical_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS award_vendor_map (
    run_id TEXT NOT NULL,
    award_id TEXT NOT NULL,
    vendor_id TEXT NOT NULL,
    PRIMARY KEY (run_id, award_id)
);

CREATE TABLE IF NOT EXISTS monthly_vendor_spend (
    run_id TEXT NOT NULL,
    vendor_id TEXT NOT NULL,
    year_month TEXT NOT NULL,
    obligation_sum DECIMAL(18,2),
    award_count INTEGER,
    avg_award_size DECIMAL(18,2),
    rolling_3m_mean DECIMAL(18,2),
    rolling_3m_mad DECIMAL(18,2),
    PRIMARY KEY (run_id, vendor_id, year_month)
);

CREATE INDEX IF NOT EXISTS idx_raw_awards_run_id ON raw_awards(run_id);
CREATE INDEX IF NOT EXISTS idx_award_vendor_map_vendor ON award_vendor_map(vendor_id);
