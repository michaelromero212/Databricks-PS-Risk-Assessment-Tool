import React, { useState, useCallback } from 'react';

/**
 * Import Data Page
 * Allows PS members to upload their engagement data via CSV files
 */
function ImportData() {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [dragActive, setDragActive] = useState(false);

    // Handle file selection
    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setError(null);
            setResult(null);
        }
    };

    // Handle drag events
    const handleDrag = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') {
            setDragActive(true);
        } else if (e.type === 'dragleave') {
            setDragActive(false);
        }
    }, []);

    // Handle drop
    const handleDrop = useCallback((e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);

        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const droppedFile = e.dataTransfer.files[0];
            if (droppedFile.name.endsWith('.csv')) {
                setFile(droppedFile);
                setError(null);
                setResult(null);
            } else {
                setError('Please upload a CSV file');
            }
        }
    }, []);

    // Handle upload
    const handleUpload = async () => {
        if (!file) {
            setError('Please select a file first');
            return;
        }

        setUploading(true);
        setError(null);
        setResult(null);

        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/import/engagements', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (response.ok) {
                setResult(data);
                setFile(null);
                // Reset file input
                const fileInput = document.getElementById('file-input');
                if (fileInput) fileInput.value = '';
            } else {
                setError(data.error || 'Failed to import file');
            }
        } catch (err) {
            setError(err.message || 'Upload failed');
        } finally {
            setUploading(false);
        }
    };

    // Download template
    const downloadTemplate = (type) => {
        window.open(`/api/import/templates/${type}`, '_blank');
    };

    return (
        <div className="import-data-page">
            <div className="page-header">
                <h1>Import Engagement Data</h1>
                <p className="page-subtitle">
                    Upload your engagement data as a CSV file to get AI-powered risk assessments
                </p>
            </div>

            {/* Instructions */}
            <div className="import-instructions card">
                <h2>How It Works</h2>
                <ol className="import-steps">
                    <li>
                        <span className="step-number">1</span>
                        <div className="step-content">
                            <strong>Download the template</strong>
                            <p>Get the sample CSV template with the correct format</p>
                        </div>
                    </li>
                    <li>
                        <span className="step-number">2</span>
                        <div className="step-content">
                            <strong>Fill in your data</strong>
                            <p>Add your engagement details: customer name, industry, dates, SA info</p>
                        </div>
                    </li>
                    <li>
                        <span className="step-number">3</span>
                        <div className="step-content">
                            <strong>Upload the file</strong>
                            <p>Drop your CSV here and the system will calculate risk scores automatically</p>
                        </div>
                    </li>
                </ol>

                <div className="template-downloads">
                    <h3>Download Templates</h3>
                    <div className="template-buttons">
                        <button
                            className="btn btn-secondary"
                            onClick={() => downloadTemplate('engagements')}
                        >
                            📄 Engagement Template
                        </button>
                    </div>
                </div>
            </div>

            {/* Upload Area */}
            <div className="import-upload-section card">
                <h2>Upload Engagement Data</h2>

                <div
                    className={`file-dropzone ${dragActive ? 'drag-active' : ''} ${file ? 'has-file' : ''}`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                >
                    <input
                        type="file"
                        id="file-input"
                        accept=".csv"
                        onChange={handleFileChange}
                        style={{ display: 'none' }}
                    />

                    {file ? (
                        <div className="file-selected">
                            <span className="file-icon">📁</span>
                            <span className="file-name">{file.name}</span>
                            <span className="file-size">({(file.size / 1024).toFixed(1)} KB)</span>
                            <button
                                className="btn btn-ghost btn-sm"
                                onClick={() => {
                                    setFile(null);
                                    const fileInput = document.getElementById('file-input');
                                    if (fileInput) fileInput.value = '';
                                }}
                            >
                                ✕
                            </button>
                        </div>
                    ) : (
                        <div className="dropzone-content">
                            <span className="dropzone-icon">📤</span>
                            <p className="dropzone-text">
                                Drag and drop your CSV file here, or{' '}
                                <label htmlFor="file-input" className="dropzone-link">
                                    browse
                                </label>
                            </p>
                            <p className="dropzone-hint">Supports CSV files up to 16MB</p>
                        </div>
                    )}
                </div>

                <button
                    className="btn btn-primary btn-upload"
                    onClick={handleUpload}
                    disabled={!file || uploading}
                >
                    {uploading ? 'Uploading...' : 'Upload & Process'}
                </button>
            </div>

            {/* Error Display */}
            {error && (
                <div className="import-error card">
                    <span className="error-icon">⚠️</span>
                    <span className="error-message">{error}</span>
                </div>
            )}

            {/* Success Result */}
            {result && (
                <div className="import-result card">
                    <div className="result-header">
                        <span className="success-icon">✅</span>
                        <h3>Import Successful</h3>
                    </div>

                    <div className="result-summary">
                        <div className="result-stat">
                            <span className="stat-value">{result.imported_count}</span>
                            <span className="stat-label">Engagements imported</span>
                        </div>
                        <div className="result-stat">
                            <span className="stat-value">{result.total_engagements}</span>
                            <span className="stat-label">Total engagements</span>
                        </div>
                    </div>

                    {result.imported && result.imported.length > 0 && (
                        <div className="imported-list">
                            <h4>Imported Engagements</h4>
                            <table className="import-table">
                                <thead>
                                    <tr>
                                        <th>Customer</th>
                                        <th>Risk Score</th>
                                        <th>Risk Level</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {result.imported.map((eng) => (
                                        <tr key={eng.engagement_id}>
                                            <td>{eng.customer_name}</td>
                                            <td>{eng.risk_score?.toFixed(0) || 'N/A'}</td>
                                            <td>
                                                <span className={`risk-badge-small risk-badge-${eng.risk_level?.toLowerCase()}`}>
                                                    {eng.risk_level || 'N/A'}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}

                    {result.errors && result.errors.length > 0 && (
                        <div className="import-warnings">
                            <h4>Warnings ({result.errors.length})</h4>
                            <ul>
                                {result.errors.map((err, i) => (
                                    <li key={i}>{err}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    <div className="result-actions">
                        <a href="/" className="btn btn-primary">
                            View All Engagements
                        </a>
                        <a href="/dashboard" className="btn btn-secondary">
                            Open Dashboard
                        </a>
                    </div>
                </div>
            )}

            {/* Expected Format */}
            <div className="import-format card">
                <h2>Expected CSV Format</h2>
                <p>Your CSV file should have the following columns:</p>
                <table className="format-table">
                    <thead>
                        <tr>
                            <th>Column</th>
                            <th>Required</th>
                            <th>Format / Values</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><code>customer_name</code></td>
                            <td>Yes</td>
                            <td>Company name (e.g., "Acme Corp")</td>
                        </tr>
                        <tr>
                            <td><code>industry</code></td>
                            <td>Yes</td>
                            <td>Technology, Healthcare, Financial Services, Retail, Manufacturing, Energy</td>
                        </tr>
                        <tr>
                            <td><code>start_date</code></td>
                            <td>Yes</td>
                            <td>YYYY-MM-DD (e.g., "2025-01-15")</td>
                        </tr>
                        <tr>
                            <td><code>target_completion_date</code></td>
                            <td>Yes</td>
                            <td>YYYY-MM-DD (e.g., "2025-04-15")</td>
                        </tr>
                        <tr>
                            <td><code>scope_size</code></td>
                            <td>Yes</td>
                            <td>small, medium, or large</td>
                        </tr>
                        <tr>
                            <td><code>sa_assigned</code></td>
                            <td>Yes</td>
                            <td>SA name (e.g., "John Smith")</td>
                        </tr>
                        <tr>
                            <td><code>sa_confidence_score</code></td>
                            <td>Yes</td>
                            <td>1-5 (1=low confidence, 5=high confidence)</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default ImportData;
