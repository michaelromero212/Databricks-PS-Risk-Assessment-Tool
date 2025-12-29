"""
Engagements API routes.
"""

from flask import Blueprint, jsonify, request
from backend.services.data_store import get_data_store
from backend.services.ai_explainer import get_ai_explainer
from backend.services.recommendations import get_recommendations_engine

engagements_bp = Blueprint('engagements', __name__)


@engagements_bp.route('/', methods=['GET'])
def list_engagements():
    """
    List all engagements with their current risk information.
    
    Query params:
        - risk_level: Filter by risk level (Low, Medium, High)
        - industry: Filter by industry
    """
    store = get_data_store()
    engagements = store.get_all_engagements()
    
    # Get filter params
    risk_filter = request.args.get('risk_level')
    industry_filter = request.args.get('industry')
    
    results = []
    for eng in engagements:
        risk_score = store.get_latest_risk_score(eng.engagement_id)
        
        # Apply filters
        if risk_filter and risk_score:
            if risk_score.risk_level.value != risk_filter:
                continue
        
        if industry_filter:
            if eng.industry.value != industry_filter:
                continue
        
        result = {
            "engagement_id": eng.engagement_id,
            "customer_name": eng.customer_name,
            "industry": eng.industry.value,
            "start_date": eng.start_date.isoformat(),
            "target_completion_date": eng.target_completion_date.isoformat(),
            "scope_size": eng.scope_size.value,
            "sa_assigned": eng.sa_assigned,
            "sa_confidence_score": eng.sa_confidence_score,
        }
        
        if risk_score:
            result["risk_score"] = risk_score.risk_score
            result["risk_level"] = risk_score.risk_level.value
            result["trend_direction"] = risk_score.trend_direction.value
        
        results.append(result)
    
    # Sort by risk score (highest first)
    results.sort(key=lambda x: x.get("risk_score", 0), reverse=True)
    
    return jsonify({
        "engagements": results,
        "total": len(results)
    })


@engagements_bp.route('/<engagement_id>', methods=['GET'])
def get_engagement(engagement_id):
    """
    Get detailed information for a specific engagement.
    """
    store = get_data_store()
    
    engagement = store.get_engagement(engagement_id)
    if not engagement:
        return jsonify({"error": "Engagement not found"}), 404
    
    risk_score = store.get_latest_risk_score(engagement_id)
    signals = store.get_engagement_signals(engagement_id)
    explanation = store.get_explanation(engagement_id)
    risk_history = store.get_risk_history(engagement_id)
    
    result = {
        "engagement": {
            "engagement_id": engagement.engagement_id,
            "customer_name": engagement.customer_name,
            "industry": engagement.industry.value,
            "start_date": engagement.start_date.isoformat(),
            "target_completion_date": engagement.target_completion_date.isoformat(),
            "scope_size": engagement.scope_size.value,
            "sa_assigned": engagement.sa_assigned,
            "sa_confidence_score": engagement.sa_confidence_score,
            "created_at": engagement.created_at.isoformat(),
            "updated_at": engagement.updated_at.isoformat(),
        }
    }
    
    if risk_score:
        result["risk"] = {
            "score": risk_score.risk_score,
            "level": risk_score.risk_level.value,
            "trend_direction": risk_score.trend_direction.value,
            "computed_at": risk_score.computed_at.isoformat(),
            "contributing_factors": [
                {
                    "name": f.factor_name,
                    "value": f.factor_value,
                    "weight": f.weight,
                    "impact": f.impact,
                    "description": f.description,
                }
                for f in risk_score.contributing_factors
            ],
        }
    
    if signals:
        result["signals"] = [
            {
                "date": s.signal_date.isoformat(),
                "job_success_count": s.job_success_count,
                "job_failure_count": s.job_failure_count,
                "avg_job_duration_seconds": s.avg_job_duration_seconds,
                "notebook_execution_count": s.notebook_execution_count,
                "sql_query_count": s.sql_query_count,
                "last_activity": s.last_activity_timestamp.isoformat() if s.last_activity_timestamp else None,
            }
            for s in sorted(signals, key=lambda x: x.signal_date)
        ]
    
    if explanation:
        result["ai_explanation"] = {
            "explanation": explanation.risk_explanation,
            "mitigations": explanation.mitigation_suggestions,
            "model_name": explanation.model_name,
            "model_provider": explanation.model_provider,
            "model_purpose": explanation.model_purpose,
            "status": explanation.generation_status.value,
            "cached": explanation.cached,
            "generated_at": explanation.generated_at.isoformat(),
        }
    
    # Add smart recommendations
    recommendations_engine = get_recommendations_engine()
    if risk_score:
        result["recommendations"] = recommendations_engine.get_recommendations(
            engagement, risk_score
        )
    else:
        result["recommendations"] = ["Wait for initial risk scoring to get recommendations."]
    
    if risk_history:
        result["risk_history"] = [
            {
                "score": rs.risk_score,
                "level": rs.risk_level.value,
                "computed_at": rs.computed_at.isoformat(),
            }
            for rs in risk_history
        ]
    
    return jsonify(result)


@engagements_bp.route('/<engagement_id>/risk', methods=['GET'])
def get_engagement_risk(engagement_id):
    """
    Get just the risk information for an engagement.
    """
    store = get_data_store()
    
    engagement = store.get_engagement(engagement_id)
    if not engagement:
        return jsonify({"error": "Engagement not found"}), 404
    
    risk_score = store.get_latest_risk_score(engagement_id)
    if not risk_score:
        return jsonify({"error": "No risk score available"}), 404
    
    return jsonify({
        "engagement_id": engagement_id,
        "risk_score": risk_score.risk_score,
        "risk_level": risk_score.risk_level.value,
        "trend_direction": risk_score.trend_direction.value,
        "computed_at": risk_score.computed_at.isoformat(),
        "contributing_factors": [
            {
                "name": f.factor_name,
                "value": f.factor_value,
                "weight": f.weight,
                "impact": f.impact,
                "description": f.description,
            }
            for f in risk_score.contributing_factors
        ],
    })


@engagements_bp.route('/<engagement_id>/explanation', methods=['GET'])
def get_engagement_explanation(engagement_id):
    """
    Get the AI-generated explanation for an engagement.
    """
    store = get_data_store()
    
    engagement = store.get_engagement(engagement_id)
    if not engagement:
        return jsonify({"error": "Engagement not found"}), 404
    
    explanation = store.get_explanation(engagement_id)
    if not explanation:
        return jsonify({"error": "No explanation available"}), 404
    
    return jsonify({
        "engagement_id": engagement_id,
        "explanation": explanation.risk_explanation,
        "mitigations": explanation.mitigation_suggestions,
        "model_metadata": {
            "model_name": explanation.model_name,
            "model_provider": explanation.model_provider,
            "model_purpose": explanation.model_purpose,
            "status": explanation.generation_status.value,
            "cached": explanation.cached,
            "generated_at": explanation.generated_at.isoformat(),
        }
    })
