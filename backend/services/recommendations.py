"""
Smart Recommendations Engine

Generates actionable suggestions for PS practitioners to mitigate engagement risk.
"""

from typing import List, Dict, Any
from backend.models.schemas import Engagement, RiskScore, RiskLevel, ScopeSize

class RecommendationsEngine:
    """
    Analyzes engagement data and risk scores to provide specific, 
    actionable recommendations for PS teams.
    """
    
    def get_recommendations(self, engagement: Engagement, risk_score: RiskScore) -> List[str]:
        """
        Generate recommendations based on engagement profile and risk factors.
        """
        recommendations = []
        
        # 1. High-level risk recommendations
        if risk_score.risk_score > 75:
            recommendations.append("🚨 SCHEDULE EMERGENCY REVIEW: This engagement shows critical risk indicators. Schedule a review with the Delivery Director immediately.")
        elif risk_score.risk_score > 50:
            recommendations.append("⚠️ WEEKLY SYNC: Increase cadence of internal syncs to monitor platform signals more closely.")
            
        # 2. SA Confidence based recommendations
        if engagement.sa_confidence_score <= 2:
            recommendations.append("🔍 EXPERT PEER REVIEW: SA confidence is low. Assign a Principal Architect or Fellow for a technical pier review of the architecture.")
            
        # 3. Resource/Scope alignment
        if engagement.scope_size == ScopeSize.LARGE and risk_score.risk_score > 60:
            recommendations.append("👥 RESOURCE AUDIT: Large scope engagement is showing high risk. Evaluate if additional delivery resources (Resident Architects/Engineers) are needed.")
            
        # 4. Platform signal specific recommendations
        for factor in risk_score.contributing_factors:
            if factor.impact == "negative":
                if "failure" in factor.factor_name.lower():
                    recommendations.append("🛠️ WORKLOAD OPTIMIZATION: High job failure rate detected. Conduct a Databricks Job/Cluster optimization session with the customer.")
                elif "duration" in factor.factor_name.lower():
                    recommendations.append("⚡ PERFORMANCE TUNING: Workload duration is increasing. Recommend a Photon or Graviton migration assessment for better performance.")
                elif "recency" in factor.factor_name.lower() or "activity" in factor.factor_name.lower():
                    recommendations.append("📞 CUSTOMER RE-ENGAGEMENT: Low platform activity detected. Reach out to the customer technical lead to identify delivery blockers.")

        # Default recommendation if nothing specific found
        if not recommendations:
            recommendations.append("✅ MAINTAIN MOMENTUM: Engagement is trending well. Continue current delivery cadence and monitor weekly reports.")
            
        return recommendations

# Singleton instance
_recommendations_engine = None

def get_recommendations_engine() -> RecommendationsEngine:
    """Get the singleton recommendations engine instance."""
    global _recommendations_engine
    if _recommendations_engine is None:
        _recommendations_engine = RecommendationsEngine()
    return _recommendations_engine
