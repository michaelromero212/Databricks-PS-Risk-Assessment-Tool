import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import RiskBadge from '../components/RiskBadge';
import TrendIndicator from '../components/TrendIndicator';

/**
 * EngagementOverview Page
 * Main dashboard showing all engagements with risk information
 */
function EngagementOverview() {
    const [engagements, setEngagements] = useState([]);
    const [metrics, setMetrics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filter, setFilter] = useState('all');
    const [searchTerm, setSearchTerm] = useState('');

    const navigate = useNavigate();

    // Fetch data on mount
    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);

                // Fetch engagements and metrics in parallel
                const [engRes, metRes] = await Promise.all([
                    fetch('/api/engagements'),
                    fetch('/api/metrics/summary')
                ]);

                if (!engRes.ok) throw new Error('Failed to fetch engagements');
                if (!metRes.ok) throw new Error('Failed to fetch metrics');

                const engData = await engRes.json();
                const metData = await metRes.json();

                setEngagements(engData.engagements || []);
                setMetrics(metData);
                setError(null);
            } catch (err) {
                setError(err.message);
                console.error('Error fetching data:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    // Filter engagements
    const filteredEngagements = engagements.filter(eng => {
        // Risk level filter
        if (filter !== 'all' && eng.risk_level?.toLowerCase() !== filter) {
            return false;
        }
        // Search filter
        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            return (
                eng.customer_name?.toLowerCase().includes(term) ||
                eng.industry?.toLowerCase().includes(term) ||
                eng.sa_assigned?.toLowerCase().includes(term)
            );
        }
        return true;
    });

    // Handle engagement click
    const handleEngagementClick = (id) => {
        navigate(`/engagement/${id}`);
    };

    // Loading state
    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p className="loading-text">Loading engagements...</p>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="empty-state">
                <div className="empty-state-icon">⚠️</div>
                <h2 className="empty-state-title">Error Loading Data</h2>
                <p className="empty-state-description">{error}</p>
                <button
                    className="btn btn-primary"
                    onClick={() => window.location.reload()}
                    style={{ marginTop: '20px' }}
                >
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div>
            {/* Page Header */}
            <div style={{ marginBottom: 'var(--space-6)' }}>
                <h1 style={{ marginBottom: 'var(--space-2)' }}>Engagement Risk Overview</h1>
                <p style={{ color: 'var(--color-text-secondary)', marginBottom: 0 }}>
                    Monitor delivery risk across all Professional Services engagements
                </p>
            </div>

            {/* Metrics Cards */}
            {metrics && (
                <div className="metrics-grid">
                    <div className="metric-card">
                        <span className="metric-label">Active Engagements</span>
                        <span className="metric-value highlight">{metrics.overview?.total_engagements || 0}</span>
                    </div>
                    <div className="metric-card">
                        <span className="metric-label">High Risk</span>
                        <span className="metric-value" style={{ color: 'var(--color-risk-high)' }}>
                            {metrics.risk_distribution?.high || 0}
                        </span>
                    </div>
                    <div className="metric-card">
                        <span className="metric-label">Medium Risk</span>
                        <span className="metric-value" style={{ color: 'var(--color-risk-medium)' }}>
                            {metrics.risk_distribution?.medium || 0}
                        </span>
                    </div>
                    <div className="metric-card">
                        <span className="metric-label">Low Risk</span>
                        <span className="metric-value" style={{ color: 'var(--color-risk-low)' }}>
                            {metrics.risk_distribution?.low || 0}
                        </span>
                    </div>
                    <div className="metric-card">
                        <span className="metric-label">Avg Risk Score</span>
                        <span className="metric-value">{metrics.overview?.avg_risk_score?.toFixed(1) || 0}</span>
                    </div>
                </div>
            )}

            {/* Filter Bar */}
            <div className="filter-bar">
                <div className="filter-group" role="group" aria-label="Filter by risk level">
                    <button
                        className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
                        onClick={() => setFilter('all')}
                    >
                        All
                    </button>
                    <button
                        className={`filter-btn ${filter === 'high' ? 'active' : ''}`}
                        onClick={() => setFilter('high')}
                    >
                        High Risk
                    </button>
                    <button
                        className={`filter-btn ${filter === 'medium' ? 'active' : ''}`}
                        onClick={() => setFilter('medium')}
                    >
                        Medium Risk
                    </button>
                    <button
                        className={`filter-btn ${filter === 'low' ? 'active' : ''}`}
                        onClick={() => setFilter('low')}
                    >
                        Low Risk
                    </button>
                </div>
                <input
                    type="search"
                    className="search-input"
                    placeholder="Search engagements..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    aria-label="Search engagements"
                />
            </div>

            {/* Engagement Grid */}
            {filteredEngagements.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-state-icon">📋</div>
                    <h2 className="empty-state-title">No Engagements Found</h2>
                    <p className="empty-state-description">
                        {searchTerm || filter !== 'all'
                            ? 'Try adjusting your filters or search term'
                            : 'No engagements have been loaded yet'}
                    </p>
                </div>
            ) : (
                <div className="engagement-grid">
                    {filteredEngagements.map(eng => (
                        <article
                            key={eng.engagement_id}
                            className="engagement-card"
                            onClick={() => handleEngagementClick(eng.engagement_id)}
                            onKeyPress={(e) => e.key === 'Enter' && handleEngagementClick(eng.engagement_id)}
                            tabIndex={0}
                            role="button"
                            aria-label={`View details for ${eng.customer_name}`}
                        >
                            <div className="engagement-card-header">
                                <div>
                                    <h3 className="engagement-name">{eng.customer_name}</h3>
                                    <span className="engagement-industry">{eng.industry}</span>
                                </div>
                                <RiskBadge level={eng.risk_level} />
                            </div>

                            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)', marginBottom: 'var(--space-4)' }}>
                                <div className="score-display" style={{ alignItems: 'flex-start' }}>
                                    <span
                                        className={`score-value score-${eng.risk_level?.toLowerCase()}`}
                                        style={{ fontSize: 'var(--font-size-2xl)' }}
                                    >
                                        {eng.risk_score?.toFixed(0)}
                                    </span>
                                    <span className="score-label">Risk Score</span>
                                </div>
                                <TrendIndicator direction={eng.trend_direction} />
                            </div>

                            <div className="engagement-meta">
                                <div className="engagement-meta-item">
                                    <span className="engagement-meta-label">Solution Architect</span>
                                    <span className="engagement-meta-value">{eng.sa_assigned}</span>
                                </div>
                                <div className="engagement-meta-item">
                                    <span className="engagement-meta-label">Scope</span>
                                    <span className="engagement-meta-value" style={{ textTransform: 'capitalize' }}>
                                        {eng.scope_size}
                                    </span>
                                </div>
                                <div className="engagement-meta-item">
                                    <span className="engagement-meta-label">Start Date</span>
                                    <span className="engagement-meta-value">
                                        {new Date(eng.start_date).toLocaleDateString()}
                                    </span>
                                </div>
                                <div className="engagement-meta-item">
                                    <span className="engagement-meta-label">Target Date</span>
                                    <span className="engagement-meta-value">
                                        {new Date(eng.target_completion_date).toLocaleDateString()}
                                    </span>
                                </div>
                            </div>
                        </article>
                    ))}
                </div>
            )}
        </div>
    );
}

export default EngagementOverview;
