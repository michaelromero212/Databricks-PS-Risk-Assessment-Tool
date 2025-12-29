-- =============================================================================
-- Databricks PS Risk Assessment Tool - Sample Queries
-- =============================================================================
-- Useful SQL queries for exploring and analyzing engagement risk data.
-- Run these in Databricks SQL Warehouse after tables are populated.
-- =============================================================================

USE ps_risk_assessment;

-- =============================================================================
-- Query 1: All engagements with current risk status
-- =============================================================================
SELECT 
    e.engagement_id,
    e.customer_name,
    e.industry,
    e.scope_size,
    e.sa_assigned,
    e.sa_confidence_score,
    e.start_date,
    e.target_completion_date,
    DATEDIFF(e.target_completion_date, CURRENT_DATE()) as days_remaining,
    rs.risk_score,
    rs.risk_level,
    rs.trend_direction,
    rs.computed_at as last_risk_update
FROM engagements e
LEFT JOIN (
    SELECT engagement_id, risk_score, risk_level, trend_direction, computed_at,
           ROW_NUMBER() OVER (PARTITION BY engagement_id ORDER BY computed_at DESC) as rn
    FROM risk_scores
) rs ON e.engagement_id = rs.engagement_id AND rs.rn = 1
ORDER BY rs.risk_score DESC NULLS LAST;


-- =============================================================================
-- Query 2: Risk distribution summary
-- =============================================================================
SELECT 
    risk_level,
    COUNT(*) as engagement_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM (
    SELECT engagement_id, risk_level,
           ROW_NUMBER() OVER (PARTITION BY engagement_id ORDER BY computed_at DESC) as rn
    FROM risk_scores
) latest
WHERE rn = 1
GROUP BY risk_level
ORDER BY 
    CASE risk_level 
        WHEN 'High' THEN 1 
        WHEN 'Medium' THEN 2 
        WHEN 'Low' THEN 3 
    END;


-- =============================================================================
-- Query 3: High risk engagements with AI explanations
-- =============================================================================
SELECT 
    e.customer_name,
    e.industry,
    e.sa_assigned,
    rs.risk_score,
    rs.risk_level,
    ai.risk_explanation,
    ai.mitigation_suggestions,
    ai.model_name,
    ai.generation_status
FROM engagements e
JOIN (
    SELECT engagement_id, risk_score, risk_level,
           ROW_NUMBER() OVER (PARTITION BY engagement_id ORDER BY computed_at DESC) as rn
    FROM risk_scores
    WHERE risk_level = 'High'
) rs ON e.engagement_id = rs.engagement_id AND rs.rn = 1
LEFT JOIN (
    SELECT engagement_id, risk_explanation, mitigation_suggestions, 
           model_name, generation_status,
           ROW_NUMBER() OVER (PARTITION BY engagement_id ORDER BY generated_at DESC) as rn
    FROM ai_explanations
) ai ON e.engagement_id = ai.engagement_id AND ai.rn = 1
ORDER BY rs.risk_score DESC;


-- =============================================================================
-- Query 4: Platform signal trends (last 7 days)
-- =============================================================================
SELECT 
    e.customer_name,
    ps.signal_date,
    ps.job_success_count,
    ps.job_failure_count,
    ROUND(ps.job_failure_count * 100.0 / NULLIF(ps.job_success_count + ps.job_failure_count, 0), 2) as failure_rate,
    ps.avg_job_duration_seconds,
    ps.notebook_execution_count,
    ps.sql_query_count
FROM platform_signals ps
JOIN engagements e ON ps.engagement_id = e.engagement_id
WHERE ps.signal_date >= DATE_SUB(CURRENT_DATE(), 7)
ORDER BY e.customer_name, ps.signal_date DESC;


-- =============================================================================
-- Query 5: Engagement timeline status
-- =============================================================================
SELECT 
    customer_name,
    industry,
    scope_size,
    start_date,
    target_completion_date,
    DATEDIFF(target_completion_date, start_date) as total_days,
    DATEDIFF(CURRENT_DATE(), start_date) as elapsed_days,
    DATEDIFF(target_completion_date, CURRENT_DATE()) as remaining_days,
    ROUND(DATEDIFF(CURRENT_DATE(), start_date) * 100.0 / 
          NULLIF(DATEDIFF(target_completion_date, start_date), 0), 1) as progress_pct,
    CASE 
        WHEN DATEDIFF(target_completion_date, CURRENT_DATE()) < 0 THEN 'Overdue'
        WHEN DATEDIFF(CURRENT_DATE(), start_date) * 100.0 / 
             NULLIF(DATEDIFF(target_completion_date, start_date), 0) > 80 THEN 'Critical'
        WHEN DATEDIFF(CURRENT_DATE(), start_date) * 100.0 / 
             NULLIF(DATEDIFF(target_completion_date, start_date), 0) > 50 THEN 'Mid-stage'
        ELSE 'Early'
    END as timeline_status
FROM engagements
ORDER BY remaining_days ASC;


-- =============================================================================
-- Query 6: SA workload and risk analysis
-- =============================================================================
SELECT 
    e.sa_assigned,
    COUNT(DISTINCT e.engagement_id) as total_engagements,
    SUM(CASE WHEN rs.risk_level = 'High' THEN 1 ELSE 0 END) as high_risk,
    SUM(CASE WHEN rs.risk_level = 'Medium' THEN 1 ELSE 0 END) as medium_risk,
    SUM(CASE WHEN rs.risk_level = 'Low' THEN 1 ELSE 0 END) as low_risk,
    ROUND(AVG(rs.risk_score), 2) as avg_risk_score,
    ROUND(AVG(e.sa_confidence_score), 2) as avg_confidence
FROM engagements e
LEFT JOIN (
    SELECT engagement_id, risk_score, risk_level,
           ROW_NUMBER() OVER (PARTITION BY engagement_id ORDER BY computed_at DESC) as rn
    FROM risk_scores
) rs ON e.engagement_id = rs.engagement_id AND rs.rn = 1
GROUP BY e.sa_assigned
ORDER BY high_risk DESC, avg_risk_score DESC;


-- =============================================================================
-- Query 7: Industry risk breakdown
-- =============================================================================
SELECT 
    e.industry,
    COUNT(DISTINCT e.engagement_id) as total_engagements,
    ROUND(AVG(rs.risk_score), 2) as avg_risk_score,
    SUM(CASE WHEN rs.risk_level = 'High' THEN 1 ELSE 0 END) as high_risk_count,
    ROUND(SUM(CASE WHEN rs.risk_level = 'High' THEN 1 ELSE 0 END) * 100.0 / 
          COUNT(DISTINCT e.engagement_id), 1) as high_risk_pct
FROM engagements e
LEFT JOIN (
    SELECT engagement_id, risk_score, risk_level,
           ROW_NUMBER() OVER (PARTITION BY engagement_id ORDER BY computed_at DESC) as rn
    FROM risk_scores
) rs ON e.engagement_id = rs.engagement_id AND rs.rn = 1
GROUP BY e.industry
ORDER BY avg_risk_score DESC;


-- =============================================================================
-- Query 8: AI explanation coverage
-- =============================================================================
SELECT 
    COUNT(DISTINCT e.engagement_id) as total_engagements,
    COUNT(DISTINCT ai.engagement_id) as with_explanations,
    ROUND(COUNT(DISTINCT ai.engagement_id) * 100.0 / 
          COUNT(DISTINCT e.engagement_id), 2) as coverage_rate,
    SUM(CASE WHEN ai.generation_status = 'generated_successfully' THEN 1 ELSE 0 END) as generated,
    SUM(CASE WHEN ai.generation_status = 'cached' THEN 1 ELSE 0 END) as cached,
    SUM(CASE WHEN ai.generation_status = 'temporarily_unavailable' THEN 1 ELSE 0 END) as fallback
FROM engagements e
LEFT JOIN (
    SELECT engagement_id, generation_status,
           ROW_NUMBER() OVER (PARTITION BY engagement_id ORDER BY generated_at DESC) as rn
    FROM ai_explanations
) ai ON e.engagement_id = ai.engagement_id AND ai.rn = 1;


-- =============================================================================
-- Query 9: Daily metrics trend
-- =============================================================================
SELECT 
    metric_date,
    active_engagement_count,
    high_risk_count,
    medium_risk_count,
    low_risk_count,
    ROUND(avg_risk_score, 2) as avg_risk_score,
    ROUND(ai_coverage_rate, 2) as ai_coverage_rate
FROM metrics
WHERE metric_date >= DATE_SUB(CURRENT_DATE(), 30)
ORDER BY metric_date DESC;


-- =============================================================================
-- Query 10: Top contributing risk factors
-- =============================================================================
-- Note: This requires parsing the JSON contributing_factors column
SELECT 
    factor_name,
    COUNT(*) as occurrence_count,
    ROUND(AVG(factor_impact), 2) as avg_impact
FROM (
    SELECT 
        engagement_id,
        EXPLODE(FROM_JSON(contributing_factors, 'ARRAY<STRUCT<factor_name:STRING, impact:STRING>>')) as factor
    FROM (
        SELECT engagement_id, contributing_factors,
               ROW_NUMBER() OVER (PARTITION BY engagement_id ORDER BY computed_at DESC) as rn
        FROM risk_scores
        WHERE contributing_factors IS NOT NULL
    ) latest
    WHERE rn = 1
)
LATERAL VIEW INLINE (ARRAY(factor)) t AS factor_data
GROUP BY factor_name
ORDER BY occurrence_count DESC;
