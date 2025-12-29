import React from 'react';

/**
 * AIStatusPanel Component
 * Displays AI model metadata and generation status with full transparency
 * 
 * @param {Object} metadata - AI model metadata object
 */
function AIStatusPanel({ metadata }) {
    if (!metadata) {
        return (
            <div className="ai-panel">
                <div className="ai-panel-header">
                    <div className="ai-panel-icon">🤖</div>
                    <div className="ai-panel-title">AI Explanation</div>
                    <div className="ai-panel-status">
                        <span className="ai-status-dot unavailable"></span>
                        <span>Not available</span>
                    </div>
                </div>
                <p style={{ color: 'var(--color-text-muted)' }}>
                    AI explanation has not been generated for this engagement.
                </p>
            </div>
        );
    }

    const {
        model_name,
        model_provider,
        model_purpose,
        status,
        cached,
        generated_at
    } = metadata;

    // Determine status display
    const getStatusInfo = () => {
        if (cached) {
            return {
                dotClass: 'cached',
                label: 'Cached Output'
            };
        }
        switch (status) {
            case 'generated_successfully':
                return {
                    dotClass: '',
                    label: 'Generated Successfully'
                };
            case 'temporarily_unavailable':
                return {
                    dotClass: 'unavailable',
                    label: 'Using Fallback (Model Unavailable)'
                };
            default:
                return {
                    dotClass: '',
                    label: status
                };
        }
    };

    const statusInfo = getStatusInfo();

    // Format timestamp
    const formatDate = (isoString) => {
        if (!isoString) return 'N/A';
        const date = new Date(isoString);
        return date.toLocaleString();
    };

    return (
        <div className="ai-panel">
            <div className="ai-panel-header">
                <div className="ai-panel-icon">🤖</div>
                <div className="ai-panel-title">AI Model Information</div>
                <div className="ai-panel-status">
                    <span className={`ai-status-dot ${statusInfo.dotClass}`}></span>
                    <span>{statusInfo.label}</span>
                </div>
            </div>

            <div className="ai-metadata">
                <div className="ai-metadata-item">
                    <span className="ai-metadata-label">Model Name</span>
                    <span className="ai-metadata-value">{model_name}</span>
                </div>

                <div className="ai-metadata-item">
                    <span className="ai-metadata-label">Provider</span>
                    <span className="ai-metadata-value">{model_provider}</span>
                </div>

                <div className="ai-metadata-item">
                    <span className="ai-metadata-label">Purpose</span>
                    <span className="ai-metadata-value">{model_purpose}</span>
                </div>

                <div className="ai-metadata-item">
                    <span className="ai-metadata-label">Generated At</span>
                    <span className="ai-metadata-value">{formatDate(generated_at)}</span>
                </div>
            </div>
        </div>
    );
}

export default AIStatusPanel;
