import React from 'react';

/**
 * FactorList Component
 * Displays contributing factors for risk score
 * 
 * @param {Array} factors - Array of contributing factor objects
 */
function FactorList({ factors }) {
    if (!factors || factors.length === 0) {
        return (
            <div className="empty-state">
                <p className="empty-state-description">No contributing factors available</p>
            </div>
        );
    }

    return (
        <ul className="factor-list" aria-label="Contributing factors">
            {factors.map((factor, index) => (
                <li key={index} className="factor-item">
                    <div
                        className={`factor-impact ${factor.impact}`}
                        aria-label={`Impact: ${factor.impact}`}
                    ></div>
                    <div className="factor-content">
                        <div className="factor-name">{factor.name}</div>
                        <div className="factor-description">{factor.description}</div>
                    </div>
                    <div className="factor-weight">
                        {(factor.weight * 100).toFixed(0)}%
                    </div>
                </li>
            ))}
        </ul>
    );
}

export default FactorList;
