import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import RiskBadge from '../components/RiskBadge';
import TrendIndicator from '../components/TrendIndicator';
import AIStatusPanel from '../components/AIStatusPanel';
import FactorList from '../components/FactorList';
import MitigationList from '../components/MitigationList';

/**
 * EngagementDetail Page
 * Detailed view of a single engagement with risk analysis and AI explanation
 */
function EngagementDetail() {
    const { id } = useParams();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchEngagement = async () => {
            try {
                setLoading(true);
                const response = await fetch(`/api/engagements/${id}`);

                if (!response.ok) {
                    if (response.status === 404) {
                        throw new Error('Engagement not found');
                    }
                    throw new Error('Failed to fetch engagement details');
                }

                const result = await response.json();
                setData(result);
                setError(null);
            } catch (err) {
                setError(err.message);
                console.error('Error fetching engagement:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchEngagement();
    }, [id]);

    // Loading state
    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p className="loading-text">Loading engagement details...</p>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="empty-state">
                <div className="empty-state-icon">⚠️</div>
                <h2 className="empty-state-title">Error</h2>
                <p className="empty-state-description">{error}</p>
                <Link to="/" className="btn btn-primary" style={{ marginTop: '20px' }}>
                    Back to Overview
                </Link>
            </div>
        );
    }

    if (!data) return null;

    const { engagement, risk, signals, ai_explanation } = data;

    // Format date helper
    const formatDate = (dateStr) => {
        if (!dateStr) return 'N/A';
        return new Date(dateStr).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    };

    // Calculate days remaining
    const getDaysInfo = () => {
        const today = new Date();
        const target = new Date(engagement.target_completion_date);
        const start = new Date(engagement.start_date);
        const totalDays = Math.ceil((target - start) / (1000 * 60 * 60 * 24));
        const elapsed = Math.ceil((today - start) / (1000 * 60 * 60 * 24));
        const remaining = Math.ceil((target - today) / (1000 * 60 * 60 * 24));
        const progress = Math.min(100, Math.max(0, (elapsed / totalDays) * 100));

        return { totalDays, elapsed, remaining, progress };
    };

    const daysInfo = getDaysInfo();

    return (
        <div>
            {/* Breadcrumb */}
            <nav className="detail-breadcrumb" aria-label="Breadcrumb">
                <Link to="/">Engagements</Link>
                <span aria-hidden="true">/</span>
                <span aria-current="page">{engagement.customer_name}</span>
            </nav>

            {/* Header */}
            <header className="detail-header">
                <div className="detail-title-row">
                    <h1 className="detail-title">{engagement.customer_name}</h1>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
                        <RiskBadge level={risk?.level} />
                        <TrendIndicator direction={risk?.trend_direction} />
                    </div>
                </div>
                <p style={{ color: 'var(--color-text-secondary)', marginTop: 'var(--space-2)', marginBottom: 0 }}>
                    {engagement.industry} • {engagement.scope_size} scope • Assigned to {engagement.sa_assigned}
                </p>
            </header>

            <div className="detail-grid">
                {/* Main Content */}
                <div>
                    {/* Risk Score Card */}
                    <section className="card detail-section">
                        <h2 className="detail-section-title">
                            <span>📊</span> Risk Assessment
                        </h2>

                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-8)', marginBottom: 'var(--space-6)' }}>
                            <div className="score-display">
                                <span className={`score-value score-${risk?.level?.toLowerCase()}`}>
                                    {risk?.score?.toFixed(0)}
                                </span>
                                <span className="score-label">out of 100</span>
                            </div>

                            <div style={{ flex: 1 }}>
                                <div style={{
                                    height: '8px',
                                    background: 'var(--color-bg-tertiary)',
                                    borderRadius: 'var(--radius-full)',
                                    overflow: 'hidden'
                                }}>
                                    <div style={{
                                        height: '100%',
                                        width: `${risk?.score || 0}%`,
                                        background: risk?.level === 'High'
                                            ? 'var(--color-risk-high)'
                                            : risk?.level === 'Medium'
                                                ? 'var(--color-risk-medium)'
                                                : 'var(--color-risk-low)',
                                        borderRadius: 'var(--radius-full)',
                                        transition: 'width 0.5s ease'
                                    }}></div>
                                </div>
                                <div style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    marginTop: 'var(--space-2)',
                                    fontSize: 'var(--font-size-xs)',
                                    color: 'var(--color-text-muted)'
                                }}>
                                    <span>Low Risk</span>
                                    <span>Medium Risk</span>
                                    <span>High Risk</span>
                                </div>
                            </div>
                        </div>

                        <h3 style={{ fontSize: 'var(--font-size-base)', marginBottom: 'var(--space-3)' }}>
                            Contributing Factors
                        </h3>
                        <FactorList factors={risk?.contributing_factors} />
                    </section>

                    {/* AI Explanation */}
                    <section className="card detail-section">
                        <h2 className="detail-section-title">
                            <span>🤖</span> AI Risk Analysis
                        </h2>

                        {ai_explanation ? (
                            <>
                                <div style={{
                                    background: 'var(--color-bg-tertiary)',
                                    padding: 'var(--space-4)',
                                    borderRadius: 'var(--radius-md)',
                                    marginBottom: 'var(--space-6)'
                                }}>
                                    <p style={{
                                        color: 'var(--color-text-primary)',
                                        lineHeight: 'var(--line-height-relaxed)',
                                        marginBottom: 0
                                    }}>
                                        {ai_explanation.explanation}
                                    </p>
                                </div>

                                <h3 style={{ fontSize: 'var(--font-size-base)', marginBottom: 'var(--space-3)' }}>
                                    Suggested Mitigation Actions
                                </h3>
                                <MitigationList mitigations={ai_explanation.mitigations} />
                            </>
                        ) : (
                            <p style={{ color: 'var(--color-text-muted)' }}>
                                AI explanation not available for this engagement.
                            </p>
                        )}
                    </section>

                    {/* Platform Signals */}
                    <section className="card detail-section">
                        <h2 className="detail-section-title">
                            <span>📈</span> Platform Activity Signals
                        </h2>

                        {signals && signals.length > 0 ? (
                            <div style={{ overflowX: 'auto' }}>
                                <table className="data-table">
                                    <thead>
                                        <tr>
                                            <th>Date</th>
                                            <th>Jobs ✓</th>
                                            <th>Jobs ✗</th>
                                            <th>Avg Duration</th>
                                            <th>Notebooks</th>
                                            <th>SQL Queries</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {signals.slice(-7).reverse().map((signal, idx) => (
                                            <tr key={idx}>
                                                <td>{formatDate(signal.date)}</td>
                                                <td style={{ color: 'var(--color-success)' }}>{signal.job_success_count}</td>
                                                <td style={{ color: signal.job_failure_count > 0 ? 'var(--color-error)' : 'inherit' }}>
                                                    {signal.job_failure_count}
                                                </td>
                                                <td>{signal.avg_job_duration_seconds?.toFixed(1)}s</td>
                                                <td>{signal.notebook_execution_count}</td>
                                                <td>{signal.sql_query_count}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        ) : (
                            <p style={{ color: 'var(--color-text-muted)' }}>
                                No platform signals available.
                            </p>
                        )}
                    </section>
                </div>

                {/* Sidebar */}
                <aside>
                    {/* AI Model Status */}
                    <div className="detail-section">
                        <AIStatusPanel metadata={ai_explanation?.model_metadata || (ai_explanation ? {
                            model_name: ai_explanation.model_name,
                            model_provider: ai_explanation.model_provider,
                            model_purpose: ai_explanation.model_purpose,
                            status: ai_explanation.status,
                            cached: ai_explanation.cached,
                            generated_at: ai_explanation.generated_at
                        } : null)} />
                    </div>

                    {/* Engagement Details */}
                    <div className="card detail-section">
                        <h3 style={{ fontSize: 'var(--font-size-base)', marginBottom: 'var(--space-4)' }}>
                            Engagement Details
                        </h3>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                            <div>
                                <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                    Industry
                                </div>
                                <div style={{ color: 'var(--color-text-primary)', marginTop: 'var(--space-1)' }}>
                                    {engagement.industry}
                                </div>
                            </div>

                            <div>
                                <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                    Scope Size
                                </div>
                                <div style={{ color: 'var(--color-text-primary)', marginTop: 'var(--space-1)', textTransform: 'capitalize' }}>
                                    {engagement.scope_size}
                                </div>
                            </div>

                            <div>
                                <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                    Solution Architect
                                </div>
                                <div style={{ color: 'var(--color-text-primary)', marginTop: 'var(--space-1)' }}>
                                    {engagement.sa_assigned}
                                </div>
                            </div>

                            <div>
                                <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                    SA Confidence Score
                                </div>
                                <div style={{ color: 'var(--color-text-primary)', marginTop: 'var(--space-1)' }}>
                                    {engagement.sa_confidence_score} / 5
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Timeline */}
                    <div className="card">
                        <h3 style={{ fontSize: 'var(--font-size-base)', marginBottom: 'var(--space-4)' }}>
                            Timeline
                        </h3>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                            <div>
                                <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>
                                    Start Date
                                </div>
                                <div style={{ color: 'var(--color-text-primary)' }}>
                                    {formatDate(engagement.start_date)}
                                </div>
                            </div>

                            <div>
                                <div style={{ fontSize: 'var(--font-size-xs)', color: 'var(--color-text-muted)' }}>
                                    Target Completion
                                </div>
                                <div style={{ color: 'var(--color-text-primary)' }}>
                                    {formatDate(engagement.target_completion_date)}
                                </div>
                            </div>

                            <div style={{ marginTop: 'var(--space-2)' }}>
                                <div style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    marginBottom: 'var(--space-1)',
                                    fontSize: 'var(--font-size-sm)'
                                }}>
                                    <span style={{ color: 'var(--color-text-muted)' }}>Progress</span>
                                    <span style={{ color: 'var(--color-text-primary)' }}>
                                        {daysInfo.progress.toFixed(0)}%
                                    </span>
                                </div>
                                <div style={{
                                    height: '6px',
                                    background: 'var(--color-bg-tertiary)',
                                    borderRadius: 'var(--radius-full)',
                                    overflow: 'hidden'
                                }}>
                                    <div style={{
                                        height: '100%',
                                        width: `${daysInfo.progress}%`,
                                        background: daysInfo.progress > 80 ? 'var(--color-warning)' : 'var(--color-primary)',
                                        borderRadius: 'var(--radius-full)'
                                    }}></div>
                                </div>
                            </div>

                            <div style={{
                                marginTop: 'var(--space-2)',
                                padding: 'var(--space-3)',
                                background: 'var(--color-bg-tertiary)',
                                borderRadius: 'var(--radius-md)',
                                textAlign: 'center'
                            }}>
                                <div style={{
                                    fontSize: 'var(--font-size-2xl)',
                                    fontWeight: 'var(--font-weight-bold)',
                                    color: daysInfo.remaining < 0 ? 'var(--color-error)' : 'var(--color-text-primary)'
                                }}>
                                    {daysInfo.remaining < 0 ? Math.abs(daysInfo.remaining) : daysInfo.remaining}
                                </div>
                                <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-muted)' }}>
                                    {daysInfo.remaining < 0 ? 'days overdue' : 'days remaining'}
                                </div>
                            </div>
                        </div>
                    </div>
                </aside>
            </div>
        </div>
    );
}

export default EngagementDetail;
