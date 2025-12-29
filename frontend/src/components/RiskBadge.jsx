import React from 'react';

/**
 * RiskBadge Component
 * Displays a color-coded badge for risk level with accessibility support
 * 
 * @param {string} level - Risk level: 'Low', 'Medium', or 'High'
 * @param {string} size - Size variant: 'small' or 'default'
 */
function RiskBadge({ level, size = 'default' }) {
    const levelLower = level?.toLowerCase() || 'low';
    const className = `risk-badge risk-badge-${levelLower}`;

    // Include text label for screen readers and color-blind users
    const ariaLabel = `Risk level: ${level}`;

    return (
        <span
            className={className}
            role="status"
            aria-label={ariaLabel}
            style={size === 'small' ? { fontSize: '0.75rem', padding: '2px 8px' } : {}}
        >
            {level}
        </span>
    );
}

export default RiskBadge;
