CREATE TABLE IF NOT EXISTS viewers (
    viewer_id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    status TEXT NOT NULL DEFAULT 'active',
    public_rank_enabled BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS videos (
    video_id UUID PRIMARY KEY,
    creator_id UUID NOT NULL,
    published_at TIMESTAMPTZ NOT NULL,
    duration_ms BIGINT NOT NULL CHECK (duration_ms > 0),
    language TEXT,
    topic_vector_ref TEXT,
    status TEXT NOT NULL DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS video_exposures (
    exposure_id UUID PRIMARY KEY,
    viewer_id UUID NOT NULL REFERENCES viewers(viewer_id),
    video_id UUID NOT NULL REFERENCES videos(video_id),
    surface TEXT NOT NULL,
    surface_position INTEGER,
    exposed_at TIMESTAMPTZ NOT NULL,
    quality_snapshot DOUBLE PRECISION CHECK (quality_snapshot BETWEEN 0 AND 1),
    popularity_percentile DOUBLE PRECISION CHECK (popularity_percentile BETWEEN 0 AND 1),
    video_views_snapshot BIGINT CHECK (video_views_snapshot >= 0),
    creator_followers_snapshot BIGINT CHECK (creator_followers_snapshot >= 0),
    experiment_context JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_exposures_viewer_time ON video_exposures(viewer_id, exposed_at DESC);
CREATE INDEX IF NOT EXISTS idx_exposures_video_time ON video_exposures(video_id, exposed_at DESC);

CREATE TABLE IF NOT EXISTS watch_sessions (
    watch_session_id UUID PRIMARY KEY,
    viewer_id UUID NOT NULL REFERENCES viewers(viewer_id),
    video_id UUID NOT NULL REFERENCES videos(video_id),
    exposure_id UUID REFERENCES video_exposures(exposure_id),
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    effective_watch_ms BIGINT NOT NULL DEFAULT 0 CHECK (effective_watch_ms >= 0),
    max_position_ms BIGINT NOT NULL DEFAULT 0 CHECK (max_position_ms >= 0),
    completion_ratio DOUBLE PRECISION CHECK (completion_ratio BETWEEN 0 AND 1),
    active_ratio DOUBLE PRECISION CHECK (active_ratio BETWEEN 0 AND 1),
    rewatch_ratio DOUBLE PRECISION CHECK (rewatch_ratio >= 0),
    CHECK (ended_at IS NULL OR ended_at >= started_at)
);

CREATE TABLE IF NOT EXISTS video_quality_snapshots (
    video_id UUID NOT NULL REFERENCES videos(video_id),
    snapshot_at TIMESTAMPTZ NOT NULL,
    age_bucket TEXT NOT NULL,
    raw_quality DOUBLE PRECISION NOT NULL CHECK (raw_quality BETWEEN 0 AND 1),
    posterior_quality DOUBLE PRECISION NOT NULL CHECK (posterior_quality BETWEEN 0 AND 1),
    confidence DOUBLE PRECISION NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    view_count BIGINT NOT NULL CHECK (view_count >= 0),
    qualified_view_count BIGINT NOT NULL CHECK (qualified_view_count >= 0),
    PRIMARY KEY(video_id, snapshot_at)
);

CREATE TABLE IF NOT EXISTS matured_selections (
    viewer_id UUID NOT NULL REFERENCES viewers(viewer_id),
    video_id UUID NOT NULL REFERENCES videos(video_id),
    selected_at TIMESTAMPTZ NOT NULL,
    maturity_horizon_days INTEGER NOT NULL CHECK (maturity_horizon_days > 0),
    watch_depth DOUBLE PRECISION NOT NULL CHECK (watch_depth BETWEEN 0 AND 1),
    quality_at_selection DOUBLE PRECISION CHECK (quality_at_selection BETWEEN 0 AND 1),
    popularity_at_selection DOUBLE PRECISION CHECK (popularity_at_selection BETWEEN 0 AND 1),
    matured_quality DOUBLE PRECISION NOT NULL CHECK (matured_quality BETWEEN 0 AND 1),
    matured_quality_confidence DOUBLE PRECISION NOT NULL CHECK (matured_quality_confidence BETWEEN 0 AND 1),
    expected_quality DOUBLE PRECISION NOT NULL CHECK (expected_quality BETWEEN 0 AND 1),
    selection_alpha DOUBLE PRECISION NOT NULL CHECK (selection_alpha BETWEEN -1 AND 1),
    early_factor DOUBLE PRECISION NOT NULL CHECK (early_factor BETWEEN 0 AND 1),
    discovery_credit DOUBLE PRECISION NOT NULL CHECK (discovery_credit BETWEEN 0 AND 1),
    fraud_weight DOUBLE PRECISION NOT NULL DEFAULT 1.0 CHECK (fraud_weight BETWEEN 0 AND 1),
    PRIMARY KEY(viewer_id, video_id, maturity_horizon_days)
);

CREATE TABLE IF NOT EXISTS viewer_rank_snapshots (
    viewer_id UUID NOT NULL REFERENCES viewers(viewer_id),
    topic_id TEXT NOT NULL DEFAULT 'global',
    calculated_at TIMESTAMPTZ NOT NULL,
    scoring_version TEXT NOT NULL,
    viewer_rank DOUBLE PRECISION NOT NULL CHECK (viewer_rank BETWEEN 0 AND 100),
    taste DOUBLE PRECISION NOT NULL CHECK (taste BETWEEN 0 AND 1),
    discovery DOUBLE PRECISION NOT NULL CHECK (discovery BETWEEN 0 AND 1),
    depth DOUBLE PRECISION NOT NULL CHECK (depth BETWEEN 0 AND 1),
    reliability DOUBLE PRECISION NOT NULL CHECK (reliability BETWEEN 0 AND 1),
    breadth DOUBLE PRECISION NOT NULL CHECK (breadth BETWEEN 0 AND 1),
    influence DOUBLE PRECISION NOT NULL CHECK (influence BETWEEN 0 AND 1),
    confidence DOUBLE PRECISION NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    fraud_penalty DOUBLE PRECISION NOT NULL CHECK (fraud_penalty >= 0),
    sample_count BIGINT NOT NULL CHECK (sample_count >= 0),
    PRIMARY KEY(viewer_id, topic_id, calculated_at)
);
