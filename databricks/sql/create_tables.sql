-- =============================================================================
-- Databricks PS Risk Assessment Tool - Delta Table Creation
-- =============================================================================
-- Run this SQL in a Databricks SQL Warehouse to create the required tables.
-- Ensure you have a catalog and schema set up before running.
-- =============================================================================

-- Create schema (if not exists)
CREATE SCHEMA IF NOT EXISTS ps_risk_assessment;
USE ps_risk_assessment;

-- =============================================================================
-- Table: engagements
-- Stores engagement metadata for all PS customer engagements
-- =============================================================================
CREATE TABLE IF NOT EXISTS engagements (
    engagement_id STRING NOT NULL COMMENT 'Unique engagement identifier',
    customer_name STRING NOT NULL COMMENT 'Customer/company name',
    industry STRING NOT NULL COMMENT 'Industry category',
    start_date DATE NOT NULL COMMENT 'Engagement start date',
    target_completion_date DATE NOT NULL COMMENT 'Target completion date',
    scope_size STRING NOT NULL COMMENT 'Scope: small, medium, or large',
    sa_assigned STRING NOT NULL COMMENT 'Assigned Solution Architect',
    sa_confidence_score INT NOT NULL COMMENT 'SA self-reported confidence (1-5)',
    created_at TIMESTAMP DEFAULT current_timestamp() COMMENT 'Record creation timestamp',
    updated_at TIMESTAMP DEFAULT current_timestamp() COMMENT 'Last update timestamp',
    
    CONSTRAINT pk_engagements PRIMARY KEY (engagement_id),
    CONSTRAINT chk_scope CHECK (scope_size IN ('small', 'medium', 'large')),
    CONSTRAINT chk_confidence CHECK (sa_confidence_score BETWEEN 1 AND 5)
)
USING DELTA
COMMENT 'PS engagement metadata table'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =============================================================================
-- Table: platform_signals
-- Stores daily Databricks platform telemetry signals per engagement
-- =============================================================================
CREATE TABLE IF NOT EXISTS platform_signals (
    signal_id STRING NOT NULL COMMENT 'Unique signal record identifier',
    engagement_id STRING NOT NULL COMMENT 'Related engagement ID',
    signal_date DATE NOT NULL COMMENT 'Date of signal collection',
    job_success_count INT DEFAULT 0 COMMENT 'Number of successful job runs',
    job_failure_count INT DEFAULT 0 COMMENT 'Number of failed job runs',
    avg_job_duration_seconds DOUBLE DEFAULT 0 COMMENT 'Average job duration in seconds',
    notebook_execution_count INT DEFAULT 0 COMMENT 'Number of notebook executions',
    sql_query_count INT DEFAULT 0 COMMENT 'Number of SQL queries executed',
    last_activity_timestamp TIMESTAMP COMMENT 'Most recent platform activity',
    collected_at TIMESTAMP DEFAULT current_timestamp() COMMENT 'When signal was collected',
    
    CONSTRAINT pk_signals PRIMARY KEY (signal_id),
    CONSTRAINT fk_signal_engagement FOREIGN KEY (engagement_id) 
        REFERENCES engagements(engagement_id)
)
USING DELTA
COMMENT 'Daily platform activity signals per engagement'
PARTITIONED BY (signal_date)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =============================================================================
-- Table: risk_scores
-- Stores computed risk scores with contributing factors
-- =============================================================================
CREATE TABLE IF NOT EXISTS risk_scores (
    score_id STRING NOT NULL COMMENT 'Unique score record identifier',
    engagement_id STRING NOT NULL COMMENT 'Related engagement ID',
    risk_score DOUBLE NOT NULL COMMENT 'Computed risk score (0-100)',
    risk_level STRING NOT NULL COMMENT 'Risk level: Low, Medium, or High',
    contributing_factors STRING COMMENT 'JSON array of contributing factors',
    trend_direction STRING NOT NULL COMMENT 'Trend: improving, stable, or degrading',
    computed_at TIMESTAMP DEFAULT current_timestamp() COMMENT 'When score was computed',
    
    CONSTRAINT pk_risk_scores PRIMARY KEY (score_id),
    CONSTRAINT fk_risk_engagement FOREIGN KEY (engagement_id) 
        REFERENCES engagements(engagement_id),
    CONSTRAINT chk_risk_level CHECK (risk_level IN ('Low', 'Medium', 'High')),
    CONSTRAINT chk_trend CHECK (trend_direction IN ('improving', 'stable', 'degrading')),
    CONSTRAINT chk_score_range CHECK (risk_score BETWEEN 0 AND 100)
)
USING DELTA
COMMENT 'Engagement risk scores with history'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =============================================================================
-- Table: ai_explanations
-- Stores AI-generated risk explanations and mitigation suggestions
-- =============================================================================
CREATE TABLE IF NOT EXISTS ai_explanations (
    explanation_id STRING NOT NULL COMMENT 'Unique explanation identifier',
    engagement_id STRING NOT NULL COMMENT 'Related engagement ID',
    model_name STRING NOT NULL COMMENT 'Hugging Face model name used',
    model_provider STRING DEFAULT 'Hugging Face' COMMENT 'AI model provider',
    model_purpose STRING COMMENT 'Purpose of the AI model',
    risk_explanation STRING NOT NULL COMMENT 'Generated risk explanation text',
    mitigation_suggestions STRING COMMENT 'JSON array of mitigation suggestions',
    generation_status STRING NOT NULL COMMENT 'Status: generated, cached, unavailable',
    generated_at TIMESTAMP DEFAULT current_timestamp() COMMENT 'When explanation was generated',
    cached BOOLEAN DEFAULT FALSE COMMENT 'Whether this is a cached response',
    
    CONSTRAINT pk_explanations PRIMARY KEY (explanation_id),
    CONSTRAINT fk_explanation_engagement FOREIGN KEY (engagement_id) 
        REFERENCES engagements(engagement_id),
    CONSTRAINT chk_status CHECK (generation_status IN ('generated_successfully', 'cached', 'temporarily_unavailable'))
)
USING DELTA
COMMENT 'AI-generated risk explanations for engagements'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =============================================================================
-- Table: metrics
-- Stores aggregate PS metrics for leadership dashboards
-- =============================================================================
CREATE TABLE IF NOT EXISTS metrics (
    metric_id STRING NOT NULL COMMENT 'Unique metric record identifier',
    metric_date DATE NOT NULL COMMENT 'Date of metric computation',
    active_engagement_count INT DEFAULT 0 COMMENT 'Number of active engagements',
    high_risk_count INT DEFAULT 0 COMMENT 'Count of high risk engagements',
    medium_risk_count INT DEFAULT 0 COMMENT 'Count of medium risk engagements',
    low_risk_count INT DEFAULT 0 COMMENT 'Count of low risk engagements',
    avg_risk_score DOUBLE DEFAULT 0 COMMENT 'Average risk score across all engagements',
    ai_coverage_rate DOUBLE DEFAULT 0 COMMENT 'Percentage with AI explanations',
    computed_at TIMESTAMP DEFAULT current_timestamp() COMMENT 'When metrics were computed',
    
    CONSTRAINT pk_metrics PRIMARY KEY (metric_id)
)
USING DELTA
COMMENT 'Aggregate PS metrics for leadership reporting'
PARTITIONED BY (metric_date)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- =============================================================================
-- Indexes for performance
-- =============================================================================

-- Note: Delta Lake doesn't support traditional indexes, but these Z-ORDER
-- optimizations help with query performance

-- Optimize engagements table
OPTIMIZE engagements ZORDER BY (industry, sa_assigned);

-- Optimize platform_signals table
OPTIMIZE platform_signals ZORDER BY (engagement_id);

-- Optimize risk_scores table  
OPTIMIZE risk_scores ZORDER BY (engagement_id, risk_level);
