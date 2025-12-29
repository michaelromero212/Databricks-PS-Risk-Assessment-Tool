import React from 'react';

/**
 * TrendIndicator Component
 * Shows trend direction with arrow and color coding
 * 
 * @param {string} direction - Trend direction: 'improving', 'stable', or 'degrading'
 */
function TrendIndicator({ direction }) {
    const dirLower = direction?.toLowerCase() || 'stable';

    const arrows = {
        improving: '↓',
        stable: '→',
        degrading: '↑'
    };

    const labels = {
        improving: 'Improving',
        stable: 'Stable',
        degrading: 'Degrading'
    };

    return (
        <span
            className={`trend-indicator trend-${dirLower}`}
            title={`Trend: ${labels[dirLower]}`}
            aria-label={`Trend: ${labels[dirLower]}`}
        >
            <span className="trend-arrow" aria-hidden="true">
                {arrows[dirLower]}
            </span>
            <span>{labels[dirLower]}</span>
        </span>
    );
}

export default TrendIndicator;
