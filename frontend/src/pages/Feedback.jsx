import React, { useState } from 'react';

/**
 * User Feedback Page
 * Allows PS practitioners to submit feedback and feature requests.
 */
const Feedback = () => {
    const [rating, setRating] = useState(5);
    const [comment, setComment] = useState('');
    const [category, setCategory] = useState('Feature Request');
    const [email, setEmail] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [submitted, setSubmitted] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        setError(null);

        try {
            const response = await fetch('/api/feedback/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    rating,
                    comment,
                    category,
                    user_email: email
                })
            });

            if (!response.ok) throw new Error('Failed to submit feedback');

            setSubmitted(true);
        } catch (err) {
            setError(err.message);
        } finally {
            setSubmitting(false);
        }
    };

    if (submitted) {
        return (
            <div className="feedback-container card success-card">
                <div className="success-icon">✅</div>
                <h2>Thank You for Your Feedback!</h2>
                <p>Your input helps our PS AI Tooling team prioritize the right features for delivery excellence.</p>
                <button
                    className="btn btn-primary"
                    onClick={() => {
                        setSubmitted(false);
                        setComment('');
                    }}
                >
                    Submit More Feedback
                </button>
            </div>
        );
    }

    return (
        <div className="feedback-container card">
            <div className="page-header">
                <h1>PS AI Tooling Feedback</h1>
                <p className="page-subtitle">Help us innovate and improve our delivery tools</p>
            </div>

            <form className="feedback-form" onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>Category</label>
                    <select value={category} onChange={(e) => setCategory(e.target.value)}>
                        <option>Feature Request</option>
                        <option>Bug Report</option>
                        <option>General Feedback</option>
                        <option>UI/UX Suggestion</option>
                        <option>Data Quality Issue</option>
                    </select>
                </div>

                <div className="form-group">
                    <label>Rating (1-5)</label>
                    <div className="rating-input">
                        {[1, 2, 3, 4, 5].map(num => (
                            <button
                                key={num}
                                type="button"
                                className={`rating-btn ${rating >= num ? 'active' : ''}`}
                                onClick={() => setRating(num)}
                            >
                                ★
                            </button>
                        ))}
                    </div>
                </div>

                <div className="form-group">
                    <label>Your Feedback</label>
                    <textarea
                        required
                        rows="5"
                        placeholder="What would make this tool more valuable for your engagements?"
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                    ></textarea>
                </div>

                <div className="form-group">
                    <label>Email (optional)</label>
                    <input
                        type="email"
                        placeholder="yourname@databricks.com"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />
                </div>

                {error && <div className="error-message">{error}</div>}

                <button
                    type="submit"
                    className="btn btn-primary btn-block"
                    disabled={submitting}
                >
                    {submitting ? 'Submitting...' : 'Submit Assessment Tool Feedback'}
                </button>
            </form>

            <style dangerouslySetInnerHTML={{
                __html: `
                .feedback-container {
                    max-width: 600px;
                    margin: 0 auto;
                }
                .success-card {
                    text-align: center;
                    padding: var(--space-10) var(--space-6);
                }
                .success-icon {
                    font-size: 4rem;
                    margin-bottom: var(--space-4);
                }
                .form-group {
                    margin-bottom: var(--space-4);
                }
                .form-group label {
                    display: block;
                    margin-bottom: var(--space-2);
                    font-weight: var(--font-weight-bold);
                    font-size: var(--font-size-sm);
                }
                .form-group input, 
                .form-group select, 
                .form-group textarea {
                    width: 100%;
                    padding: var(--space-3);
                    border: 1px solid var(--color-border);
                    border-radius: var(--radius-md);
                    background: var(--color-bg-primary);
                    color: var(--color-text-primary);
                }
                .rating-input {
                    display: flex;
                    gap: var(--space-2);
                }
                .rating-btn {
                    background: none;
                    border: none;
                    font-size: 2rem;
                    color: var(--color-border);
                    cursor: pointer;
                    transition: color var(--transition-fast);
                }
                .rating-btn.active {
                    color: #fbbf24;
                }
                .btn-block {
                    width: 100%;
                    padding: var(--space-3);
                }
            `}} />
        </div>
    );
};

export default Feedback;
