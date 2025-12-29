import React, { useState, useEffect } from 'react';

/**
 * Databricks Workspace Status Component
 */
const WorkspaceStatus = () => {
    const [info, setInfo] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchInfo = async () => {
            try {
                const response = await fetch('/api/databricks/info');
                const data = await response.json();
                setInfo(data);
            } catch (err) {
                console.error('Failed to fetch workspace info:', err);
            } finally {
                setLoading(false);
            }
        };

        fetchInfo();
    }, []);

    if (loading) return null;
    if (!info) return null;

    return (
        <div className="workspace-status card">
            <div className="workspace-status-header">
                <div className={`status-dot ${info.connected ? 'active' : 'inactive'}`}></div>
                <div className="workspace-info">
                    <div className="workspace-host">{info.host.replace('https://', '')}</div>
                    <div className="workspace-user">{info.user_email || 'Not Connected'}</div>
                </div>
            </div>
            <div className="workspace-id">ID: {info.workspace_id || 'N/A'}</div>

            <style dangerouslySetInnerHTML={{
                __html: `
                .workspace-status {
                    padding: var(--space-3) var(--space-4);
                    margin-bottom: var(--space-6);
                    background: var(--color-bg-tertiary);
                    border: 1px solid var(--color-border);
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .workspace-status-header {
                    display: flex;
                    align-items: center;
                    gap: var(--space-3);
                }
                .status-dot {
                    width: 10px;
                    height: 10px;
                    border-radius: 50%;
                }
                .status-dot.active {
                    background: var(--color-success);
                    box-shadow: 0 0 10px var(--color-success);
                }
                .status-dot.inactive {
                    background: var(--color-error);
                }
                .workspace-host {
                    font-size: var(--font-size-sm);
                    font-weight: var(--font-weight-bold);
                    color: var(--color-text-primary);
                }
                .workspace-user {
                    font-size: var(--font-size-xs);
                    color: var(--color-text-muted);
                }
                .workspace-id {
                    font-size: var(--font-size-xs);
                    font-family: monospace;
                    color: var(--color-text-muted);
                }
            `}} />
        </div>
    );
};

export default WorkspaceStatus;
