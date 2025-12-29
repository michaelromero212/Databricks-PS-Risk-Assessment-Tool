import React, { useState, useEffect } from 'react';
import {
    PieChart, Pie, Cell, ResponsiveContainer,
    BarChart, Bar, XAxis, YAxis, Tooltip,
    LineChart, Line, ReferenceLine, Legend
} from 'recharts';
import WorkspaceStatus from '../components/WorkspaceStatus';
import ProgramImpact from '../components/ProgramImpact';
import UnityCatalogBrowser from '../components/UnityCatalogBrowser';

/**
 * Dashboard Page
 * Analytics dashboard with charts and metrics - integrated directly into React app
 */
function Dashboard() {
    const [metrics, setMetrics] = useState(null);
    const [engagements, setEngagements] = useState([]);
    const [aiStatus, setAiStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Color palette - matches light theme CSS variables
    const COLORS = {
        primary: '#e53935',
        riskHigh: '#dc2626',
        riskMedium: '#d97706',
        riskLow: '#22863a',
        text: '#1a202c',
        textSecondary: '#4a5568',
    };

    // Fetch all data on mount
    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                const [metRes, engRes, aiRes] = await Promise.all([
                    fetch('/api/metrics/summary'),
                    fetch('/api/engagements/'),
                    fetch('/api/metrics/ai-status')
                ]);

                if (metRes.ok) {
                    const metData = await metRes.json();
                    setMetrics(metData);
                }

                if (engRes.ok) {
                    const engData = await engRes.json();
                    setEngagements(engData.engagements || []);
                }

                if (aiRes.ok) {
                    const aiData = await aiRes.json();
                    setAiStatus(aiData);
                }

                setError(null);
            } catch (err) {
                setError(err.message);
                console.error('Error fetching dashboard data:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        // Refresh every 30 seconds
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, []);

    // Generate trend data (simulated historical data based on current scores)
    const generateTrendData = () => {
        if (!metrics) return [];
        const currentAvg = metrics.overview?.avg_risk_score || 50;
        const data = [];
        for (let i = 13; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            const variation = (Math.random() - 0.5) * 20;
            const score = Math.max(0, Math.min(100, currentAvg + variation - (13 - i) * 0.5));
            data.push({
                date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
                score: Math.round(score * 10) / 10
            });
        }
        return data;
    };

    // Prepare chart data
    const riskDistributionData = metrics ? [
        { name: 'High Risk', value: metrics.risk_distribution?.high || 0, color: COLORS.riskHigh },
        { name: 'Medium Risk', value: metrics.risk_distribution?.medium || 0, color: COLORS.riskMedium },
        { name: 'Low Risk', value: metrics.risk_distribution?.low || 0, color: COLORS.riskLow }
    ] : [];

    const industryData = metrics?.industries ?
        Object.entries(metrics.industries).map(([name, count]) => ({ name, count })) : [];

    const trendData = generateTrendData();

    // Loading state
    if (loading) {
        return (
            <div className="loading-container">
                <div className="loading-spinner"></div>
                <p className="loading-text">Loading dashboard...</p>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="empty-state">
                <div className="empty-state-icon">⚠️</div>
                <h2 className="empty-state-title">Error Loading Dashboard</h2>
                <p className="empty-state-description">{error}</p>
                <button className="btn btn-primary" onClick={() => window.location.reload()}>
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div className="dashboard">
            {/* Page Header */}
            <div className="dashboard-header">
                <div className="page-header">
                    <h1 className="dashboard-title">Analytics Dashboard</h1>
                    <p className="page-subtitle">Real-time insights across all Professional Services engagements</p>
                </div>
            </div>

            {/* Dashboard Metrics Cards */}
            <div className="dashboard-metrics">
                <MetricCard
                    label="Active Engagements"
                    value={metrics?.overview?.total_engagements || 0}
                    color={COLORS.primary}
                />
                <MetricCard
                    label="High Risk"
                    value={metrics?.risk_distribution?.high || 0}
                    color={COLORS.riskHigh}
                />
                <MetricCard
                    label="Medium Risk"
                    value={metrics?.risk_distribution?.medium || 0}
                    color={COLORS.riskMedium}
                />
                <MetricCard
                    label="Low Risk"
                    value={metrics?.risk_distribution?.low || 0}
                    color={COLORS.riskLow}
                />
                <MetricCard
                    label="Avg Risk Score"
                    value={(metrics?.overview?.avg_risk_score || 0).toFixed(1)}
                    subtitle="out of 100"
                />
                <MetricCard
                    label="AI Coverage"
                    value={`${(metrics?.overview?.ai_coverage || 0).toFixed(0)}% `}
                    subtitle="explanations generated"
                />
            </div>

            {/* PS Program Impact - Business ROI section (aligned with AI Tooling Role) */}
            <ProgramImpact />

            {/* Charts Section */}
            <div className="dashboard-charts-row">
                {/* Risk Distribution Pie Chart */}
                <div className="dashboard-card">
                    <h3 className="dashboard-card-title">Risk Distribution</h3>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={280}>
                            <PieChart>
                                <Pie
                                    data={riskDistributionData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={100}
                                    paddingAngle={2}
                                    dataKey="value"
                                    label={({ name, value }) => value > 0 ? `${name}: ${value} ` : ''}
                                    labelLine={false}
                                >
                                    {riskDistributionData.map((entry, index) => (
                                        <Cell key={`cell - ${index} `} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip
                                    contentStyle={{
                                        background: 'var(--color-bg-secondary)',
                                        border: '1px solid var(--color-border)',
                                        borderRadius: '8px',
                                        color: 'var(--color-text-primary)'
                                    }}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                        <div className="chart-center-label">
                            <span className="chart-center-value">
                                {metrics?.overview?.total_engagements || 0}
                            </span>
                            <span className="chart-center-text">Total</span>
                        </div>
                    </div>
                </div>

                {/* Industry Bar Chart */}
                <div className="dashboard-card">
                    <h3 className="dashboard-card-title">Engagements by Industry</h3>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={280}>
                            <BarChart
                                data={industryData}
                                layout="vertical"
                                margin={{ top: 10, right: 30, left: 80, bottom: 10 }}
                            >
                                <XAxis type="number" stroke="var(--color-text-secondary)" />
                                <YAxis
                                    type="category"
                                    dataKey="name"
                                    stroke="var(--color-text-secondary)"
                                    tick={{ fill: 'var(--color-text-secondary)', fontSize: 12 }}
                                    width={75}
                                />
                                <Tooltip
                                    contentStyle={{
                                        background: 'var(--color-bg-secondary)',
                                        border: '1px solid var(--color-border)',
                                        borderRadius: '8px',
                                        color: 'var(--color-text-primary)'
                                    }}
                                />
                                <Bar dataKey="count" fill={COLORS.primary} radius={[0, 4, 4, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Trend Chart */}
            <div className="dashboard-card dashboard-card-full">
                <h3 className="dashboard-card-title">Risk Score Trend (14 Days)</h3>
                <div className="chart-container">
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={trendData} margin={{ top: 20, right: 30, left: 20, bottom: 10 }}>
                            <XAxis
                                dataKey="date"
                                stroke="var(--color-text-secondary)"
                                tick={{ fill: 'var(--color-text-secondary)', fontSize: 11 }}
                            />
                            <YAxis
                                domain={[0, 100]}
                                stroke="var(--color-text-secondary)"
                                tick={{ fill: 'var(--color-text-secondary)', fontSize: 11 }}
                            />
                            <Tooltip
                                contentStyle={{
                                    background: 'var(--color-bg-secondary)',
                                    border: '1px solid var(--color-border)',
                                    borderRadius: '8px',
                                    color: 'var(--color-text-primary)'
                                }}
                                formatter={(value) => [`${value} `, 'Risk Score']}
                            />
                            <ReferenceLine y={35} stroke={COLORS.riskLow} strokeDasharray="5 5" label={{ value: 'Low', fill: COLORS.riskLow, fontSize: 10, position: 'right' }} />
                            <ReferenceLine y={65} stroke={COLORS.riskMedium} strokeDasharray="5 5" label={{ value: 'High', fill: COLORS.riskMedium, fontSize: 10, position: 'right' }} />
                            <Line
                                type="monotone"
                                dataKey="score"
                                stroke={COLORS.primary}
                                strokeWidth={3}
                                dot={{ fill: COLORS.primary, strokeWidth: 2, r: 4 }}
                                activeDot={{ r: 6, fill: COLORS.primary }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Bottom Row: Table and AI Status */}
            {/* Unity Catalog Browser - Live platform data demonstration */}
            <div className="dashboard-bottom-row" style={{ marginTop: 'var(--space-6)' }}>
                <UnityCatalogBrowser />
            </div>

            <div className="dashboard-bottom-row">
                {/* Engagement Table */}
                <div className="dashboard-card dashboard-card-table">
                    <h3 className="dashboard-card-title">All Engagements</h3>
                    <div className="dashboard-table-container">
                        <table className="dashboard-table">
                            <thead>
                                <tr>
                                    <th>Customer</th>
                                    <th>Industry</th>
                                    <th>Risk Level</th>
                                    <th>Score</th>
                                    <th>Trend</th>
                                    <th>SA Assigned</th>
                                </tr>
                            </thead>
                            <tbody>
                                {engagements.map((eng) => (
                                    <tr key={eng.engagement_id}>
                                        <td className="customer-name">{eng.customer_name}</td>
                                        <td>{eng.industry}</td>
                                        <td>
                                            <span className={`risk-badge-small risk-badge-${eng.risk_level?.toLowerCase()}`}>
                                                {eng.risk_level}
                                            </span>
                                        </td>
                                        <td>{eng.risk_score?.toFixed(0)}</td>
                                        <td>
                                            <TrendIndicator direction={eng.trend_direction} />
                                        </td>
                                        <td>{eng.sa_assigned}</td>
                                    </tr>
                                ))}
                                {engagements.length === 0 && (
                                    <tr>
                                        <td colSpan={6} style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-text-secondary)' }}>
                                            No engagements found
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* AI Status Panel */}
                <div className="dashboard-card dashboard-card-ai">
                    <h3 className="dashboard-card-title">AI Model Status</h3>
                    <div className="ai-status-content">
                        <div className="ai-status-indicator">
                            <span className={`ai-status-dot ${aiStatus?.model_loaded ? 'active' : 'inactive'}`}></span>
                            <span className="ai-status-text">
                                {aiStatus?.model_loaded ? 'Model Ready' : 'Standard Mode'}
                            </span>
                        </div>
                        <div className="ai-status-grid">
                            <div className="ai-status-item">
                                <span className="ai-status-label">Model Name</span>
                                <span className="ai-status-value">{aiStatus?.model_name || 'N/A'}</span>
                            </div>
                            <div className="ai-status-item">
                                <span className="ai-status-label">Provider</span>
                                <span className="ai-status-value">{aiStatus?.model_provider || 'N/A'}</span>
                            </div>
                            <div className="ai-status-item">
                                <span className="ai-status-label">Purpose</span>
                                <span className="ai-status-value">{aiStatus?.model_purpose || 'N/A'}</span>
                            </div>
                            <div className="ai-status-item">
                                <span className="ai-status-label">Cache Size</span>
                                <span className="ai-status-value">{aiStatus?.cache_size || 0} explanations</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

/**
 * Metric Card Component
 */
function MetricCard({ label, value, subtitle, color }) {
    return (
        <div className="dashboard-metric-card">
            <span className="dashboard-metric-label">{label}</span>
            <span
                className="dashboard-metric-value"
                style={color ? { color } : {}}
            >
                {value}
            </span>
            {subtitle && <span className="dashboard-metric-subtitle">{subtitle}</span>}
        </div>
    );
}

/**
 * Trend Indicator Component
 */
function TrendIndicator({ direction }) {
    const config = {
        improving: { icon: '↓', color: '#22863a', label: 'Improving' },
        stable: { icon: '→', color: '#6b7280', label: 'Stable' },
        degrading: { icon: '↑', color: '#dc2626', label: 'Degrading' }
    };
    const d = direction?.toLowerCase() || 'stable';
    const { icon, color, label } = config[d] || config.stable;

    return (
        <span style={{ color, fontSize: '0.875rem' }}>
            <span style={{ marginRight: '0.25rem' }}>{icon}</span>
            {label}
        </span>
    );
}

export default Dashboard;
