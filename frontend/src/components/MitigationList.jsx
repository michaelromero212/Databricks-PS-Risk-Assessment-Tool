import React from 'react';

/**
 * MitigationList Component
 * Displays AI-suggested mitigation actions
 * 
 * @param {Array} mitigations - Array of mitigation strings
 */
function MitigationList({ mitigations }) {
    if (!mitigations || mitigations.length === 0) {
        return (
            <div className="empty-state">
                <p className="empty-state-description">No mitigation suggestions available</p>
            </div>
        );
    }

    return (
        <ol className="mitigation-list" aria-label="Suggested mitigation actions">
            {mitigations.map((mitigation, index) => (
                <li key={index} className="mitigation-item">
                    <span className="mitigation-text">{mitigation}</span>
                </li>
            ))}
        </ol>
    );
}

export default MitigationList;
