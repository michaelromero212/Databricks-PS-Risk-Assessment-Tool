"""
Metrics API routes.
"""

from flask import Blueprint, jsonify
from backend.services.data_store import get_data_store
from backend.services.ai_explainer import get_ai_explainer



metrics_bp = Blueprint('metrics', __name__)


@metrics_bp.route('/', methods=['GET'])
def get_metrics():
    """
    Get aggregate metrics for PS leadership.
    """
    store = get_data_store()
    metrics = store.get_latest_metrics()
    
    if not metrics:
        return jsonify({"error": "No metrics available"}), 404
    
    return jsonify({
        "metric_date": metrics.metric_date.isoformat(),
        "active_engagement_count": metrics.active_engagement_count,
        "risk_distribution": {
            "high": metrics.high_risk_count,
            "medium": metrics.medium_risk_count,
            "low": metrics.low_risk_count,
        },
        "avg_risk_score": metrics.avg_risk_score,
        "ai_coverage_rate": metrics.ai_coverage_rate,
        "computed_at": metrics.computed_at.isoformat(),
    })


@metrics_bp.route('/summary', methods=['GET'])
def get_metrics_summary():
    """
    Get a summary of key metrics for dashboard display.
    """
    store = get_data_store()
    metrics = store.get_latest_metrics()
    engagements = store.get_all_engagements()
    
    # Calculate additional summaries
    industries = {}
    for eng in engagements:
        industry = eng.industry.value
        industries[industry] = industries.get(industry, 0) + 1
    
    # Get top risk factors across all engagements
    risk_factor_counts = {}
    for eng in engagements:
        risk_score = store.get_latest_risk_score(eng.engagement_id)
        if risk_score:
            for factor in risk_score.contributing_factors:
                if factor.impact == "negative":
                    name = factor.factor_name
                    risk_factor_counts[name] = risk_factor_counts.get(name, 0) + 1
    
    top_risk_factors = sorted(
        risk_factor_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    return jsonify({
        "overview": {
            "total_engagements": metrics.active_engagement_count if metrics else 0,
            "avg_risk_score": metrics.avg_risk_score if metrics else 0,
            "ai_coverage": metrics.ai_coverage_rate if metrics else 0,
        },
        "risk_distribution": {
            "high": metrics.high_risk_count if metrics else 0,
            "medium": metrics.medium_risk_count if metrics else 0,
            "low": metrics.low_risk_count if metrics else 0,
        },
        "industries": industries,
        "top_risk_factors": [
            {"factor": name, "count": count}
            for name, count in top_risk_factors
        ],
    })


@metrics_bp.route('/ai-status', methods=['GET'])
def get_ai_status():
    """
    Get the current status of the AI model.
    """
    explainer = get_ai_explainer()
    status = explainer.get_model_status()
    
    return jsonify({
        "model_name": status["model_name"],
        "model_provider": status["model_provider"],
        "model_purpose": status["model_purpose"],
        "model_loaded": status["model_loaded"],
        "cache_size": status["cache_size"],
        "available": status["available"],
        "status_message": (
            "Model loaded and ready" if status["model_loaded"]
            else "Using rule-based fallback (model not loaded)"
        )
    })


@metrics_bp.route('/program-impact', methods=['GET'])
def get_program_impact_metrics():
    """
    Get metrics showing the business impact and usage of the tool.
    Used for the PS AI Tooling implementation report.
    """
    store = get_data_store()
    stats = store.get_usage_stats()
    
    # Calculate more descriptive metrics
    return jsonify({
        "assessments_generated": stats['assessments_generated'],
        "ai_insights_delivered": stats['ai_insights_delivered'],
        "time_saved_hours": round(stats['time_saved_minutes'] / 60, 1),
        "user_adoption_rate": "85%", # Mock for demo
        "active_users_count": stats['active_users']
    })
