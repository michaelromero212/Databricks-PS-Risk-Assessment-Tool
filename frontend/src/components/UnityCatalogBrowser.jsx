import React, { useState, useEffect } from 'react';

/**
 * Unity Catalog Browser Component
 * Demonstrates integration with Databricks platform metadata.
 */
const UnityCatalogBrowser = () => {
    const [catalogs, setCatalogs] = useState([]);
    const [selectedCatalog, setSelectedCatalog] = useState(null);
    const [schemas, setSchemas] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Fetch catalogs on mount
    useEffect(() => {
        fetchCatalogs();
    }, []);

    const fetchCatalogs = async () => {
        setLoading(true);
        try {
            const response = await fetch('/api/databricks/catalogs');
            if (!response.ok) throw new Error('Failed to fetch catalogs');
            const data = await response.json();
            setCatalogs(data);

            // Auto-select first catalog if available
            if (data.length > 0 && !selectedCatalog) {
                handleCatalogClick(data[0].name);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleCatalogClick = async (catalogName) => {
        setSelectedCatalog(catalogName);
        setLoading(true);
        try {
            const response = await fetch(`/api/databricks/catalogs/${catalogName}/schemas`);
            if (!response.ok) throw new Error('Failed to fetch schemas');
            const data = await response.json();
            setSchemas(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="uc-browser card">
            <div className="card-header">
                <h3 className="card-title">Unity Catalog Browser</h3>
                <p className="card-subtitle">Browse your Databricks workspace catalogs and schemas</p>
            </div>

            <div className="uc-browser-content">
                <div className="catalog-list">
                    <h4>Catalogs</h4>
                    {catalogs.map(cat => (
                        <div
                            key={cat.name}
                            className={`catalog-item ${selectedCatalog === cat.name ? 'active' : ''}`}
                            onClick={() => handleCatalogClick(cat.name)}
                        >
                            <span className="catalog-name">{cat.name}</span>
                            <span className="schema-count badge">{cat.schema_count}</span>
                        </div>
                    ))}
                </div>

                <div className="schema-list">
                    <h4>Schemas in <strong>{selectedCatalog || '...'}</strong></h4>
                    {loading ? (
                        <div className="loading-spinner-small">Loading...</div>
                    ) : error ? (
                        <div className="error-message">{error}</div>
                    ) : schemas.length === 0 ? (
                        <p className="empty-state">Select a catalog to view schemas</p>
                    ) : (
                        <div className="schema-grid">
                            {schemas.map(schema => (
                                <div key={schema.name} className="schema-card">
                                    <div className="schema-name">{schema.name}</div>
                                    <div className="table-count">{schema.table_count} tables</div>
                                    {schema.comment && (
                                        <div className="schema-comment">{schema.comment}</div>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            <style dangerouslySetInnerHTML={{
                __html: `
                .uc-browser-content {
                    display: grid;
                    grid-template-columns: 200px 1fr;
                    gap: var(--space-6);
                    min-height: 280px;
                }
                .catalog-list {
                    border-right: 1px solid var(--color-border);
                    padding-right: var(--space-4);
                }
                .catalog-list h4 {
                    margin-bottom: var(--space-3);
                    font-size: var(--font-size-sm);
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    color: var(--color-text-muted);
                }
                .catalog-item {
                    padding: var(--space-2) var(--space-3);
                    border-radius: var(--radius-md);
                    cursor: pointer;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    gap: var(--space-2);
                    margin-bottom: var(--space-1);
                    transition: background var(--transition-fast);
                    font-size: var(--font-size-sm);
                }
                .catalog-name {
                    white-space: nowrap;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    flex: 1;
                }
                .catalog-item:hover {
                    background: var(--color-bg-hover);
                }
                .catalog-item.active {
                    background: var(--color-primary);
                    color: white;
                }
                .catalog-item.active .badge {
                    background: rgba(255,255,255,0.25);
                    color: white;
                }
                .catalog-item .badge {
                    flex-shrink: 0;
                    min-width: 24px;
                    text-align: center;
                }
                .schema-list h4 {
                    margin-bottom: var(--space-3);
                    font-size: var(--font-size-base);
                }
                .schema-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
                    gap: var(--space-3);
                }
                .schema-card {
                    background: var(--color-bg-tertiary);
                    padding: var(--space-3);
                    border-radius: var(--radius-md);
                    border: 1px solid var(--color-border);
                }
                .schema-name {
                    font-weight: var(--font-weight-bold);
                    margin-bottom: var(--space-1);
                    font-size: var(--font-size-sm);
                }
                .table-count {
                    font-size: var(--font-size-xs);
                    color: var(--color-text-muted);
                }
                .schema-comment {
                    font-size: var(--font-size-xs);
                    margin-top: var(--space-2);
                    font-style: italic;
                    color: var(--color-text-muted);
                }
                @media (max-width: 768px) {
                    .uc-browser-content {
                        grid-template-columns: 1fr;
                    }
                    .catalog-list {
                        border-right: none;
                        border-bottom: 1px solid var(--color-border);
                        padding-right: 0;
                        padding-bottom: var(--space-4);
                    }
                }
            `}} />
        </div>
    );
};

export default UnityCatalogBrowser;
