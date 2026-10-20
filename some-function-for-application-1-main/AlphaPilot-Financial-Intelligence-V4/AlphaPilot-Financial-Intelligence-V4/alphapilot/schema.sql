-- SQLite MVP data model. Move to PostgreSQL for multi-tenant production.
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS assets (
    ts_code TEXT PRIMARY KEY,
    name TEXT,
    market TEXT NOT NULL DEFAULT 'CN-A',
    industry TEXT,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS daily_bars (
    ts_code TEXT NOT NULL REFERENCES assets(ts_code),
    trade_date TEXT NOT NULL,
    open REAL NOT NULL, high REAL NOT NULL, low REAL NOT NULL,
    close REAL NOT NULL, vol REAL NOT NULL,
    adj_factor REAL NOT NULL,
    source TEXT NOT NULL DEFAULT 'Tushare',
    fetched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(ts_code, trade_date)
);
CREATE INDEX IF NOT EXISTS idx_bars_date ON daily_bars(trade_date);
CREATE TABLE IF NOT EXISTS daily_valuations (
    ts_code TEXT NOT NULL REFERENCES assets(ts_code),
    trade_date TEXT NOT NULL,
    pe_ttm REAL, pb REAL, turnover_rate REAL,
    source TEXT NOT NULL DEFAULT 'Tushare daily_basic',
    fetched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(ts_code, trade_date)
);
CREATE TABLE IF NOT EXISTS financial_facts (
    ts_code TEXT NOT NULL REFERENCES assets(ts_code),
    report_period TEXT NOT NULL,
    announced_at TEXT NOT NULL,
    available_at TEXT NOT NULL,
    metric TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT NOT NULL,
    source TEXT NOT NULL,
    PRIMARY KEY(ts_code, report_period, announced_at, metric, source)
);
CREATE TABLE IF NOT EXISTS macro_observations (
    series_id TEXT NOT NULL,
    observation_date TEXT NOT NULL,
    published_at TEXT NOT NULL,
    value REAL,
    unit TEXT,
    source TEXT NOT NULL,
    source_url TEXT,
    PRIMARY KEY(series_id, observation_date, published_at)
);
CREATE TABLE IF NOT EXISTS event_documents (
    document_id TEXT PRIMARY KEY,
    title TEXT NOT NULL, published_at TEXT NOT NULL,
    source TEXT NOT NULL, source_url TEXT,
    content TEXT, -- NULL if only title/link are licensed/available
    fetched_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS watchlists (
    watchlist_id TEXT PRIMARY KEY, owner TEXT NOT NULL,
    title TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS watchlist_members (
    watchlist_id TEXT NOT NULL REFERENCES watchlists(watchlist_id),
    ts_code TEXT NOT NULL REFERENCES assets(ts_code),
    PRIMARY KEY(watchlist_id, ts_code)
);
CREATE TABLE IF NOT EXISTS app_runs (
    run_id TEXT PRIMARY KEY,
    app_id TEXT NOT NULL, app_version TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_asof TEXT NOT NULL, status TEXT NOT NULL,
    input_json TEXT, result_json TEXT, error TEXT
);
CREATE TABLE IF NOT EXISTS signal_events (
    run_id TEXT NOT NULL REFERENCES app_runs(run_id),
    ts_code TEXT NOT NULL REFERENCES assets(ts_code),
    signal_type TEXT NOT NULL, trade_date TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    PRIMARY KEY(run_id, ts_code, signal_type, trade_date)
);
