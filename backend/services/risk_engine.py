"""
Risk Scoring Engine for Databricks PS Risk Assessment Tool.
Implements rule-based heuristics with weighted signal aggregation.
"""

from datetime import datetime, timedelta
from typing import List, Tuple
from backend.models.schemas import (
    Engagement,
    PlatformSignal,
    RiskScore,
    RiskLevel,
    TrendDirection,
    ContributingFactor,
)


class RiskEngine:
    """
    Rule-based risk scoring engine with weighted signal aggregation.
    
    Scoring Weights:
    - Job Failure Rate: 25%
    - Job Duration Trend: 15%
    - Activity Recency: 20%
    - SA Confidence: 20%
    - Schedule Variance: 20%
    
    Risk Level Thresholds:
    - Low: 0-35
    - Medium: 36-65
    - High: 66-100
    """
    
    # Scoring weights
    WEIGHTS = {
        "job_failure_rate": 0.25,
        "job_duration_trend": 0.15,
        "activity_recency": 0.20,
        "sa_confidence": 0.20,
        "schedule_variance": 0.20,
    }
    
    # Risk level thresholds
    THRESHOLD_LOW = 35
    THRESHOLD_MEDIUM = 65
    
    def __init__(self):
        """Initialize the risk engine."""
        self._cache = {}
    
    def compute_risk_score(
        self,
        engagement: Engagement,
        signals: List[PlatformSignal],
        previous_scores: List[RiskScore] = None
    ) -> RiskScore:
        """
        Compute a comprehensive risk score for an engagement.
        
        Args:
            engagement: The engagement to score
            signals: Platform signals for the engagement
            previous_scores: Previous risk scores for trend analysis
            
        Returns:
            RiskScore with computed score, level, factors, and trend
        """
        factors = []
        total_weighted_score = 0.0
        
        # 1. Job Failure Rate (25%)
        failure_score, failure_factor = self._score_job_failure_rate(signals)
        factors.append(failure_factor)
        total_weighted_score += failure_score * self.WEIGHTS["job_failure_rate"]
        
        # 2. Job Duration Trend (15%)
        duration_score, duration_factor = self._score_job_duration_trend(signals)
        factors.append(duration_factor)
        total_weighted_score += duration_score * self.WEIGHTS["job_duration_trend"]
        
        # 3. Activity Recency (20%)
        recency_score, recency_factor = self._score_activity_recency(signals)
        factors.append(recency_factor)
        total_weighted_score += recency_score * self.WEIGHTS["activity_recency"]
        
        # 4. SA Confidence (20%)
        confidence_score, confidence_factor = self._score_sa_confidence(engagement)
        factors.append(confidence_factor)
        total_weighted_score += confidence_score * self.WEIGHTS["sa_confidence"]
        
        # 5. Schedule Variance (20%)
        schedule_score, schedule_factor = self._score_schedule_variance(engagement)
        factors.append(schedule_factor)
        total_weighted_score += schedule_score * self.WEIGHTS["schedule_variance"]
        
        # Normalize to 0-100
        final_score = min(100, max(0, total_weighted_score))
        
        # Determine risk level
        risk_level = self._determine_risk_level(final_score)
        
        # Determine trend direction
        trend = self._determine_trend(final_score, previous_scores)
        
        return RiskScore(
            engagement_id=engagement.engagement_id,
            risk_score=round(final_score, 2),
            risk_level=risk_level,
            contributing_factors=factors,
            trend_direction=trend
        )
    
    def _score_job_failure_rate(
        self, signals: List[PlatformSignal]
    ) -> Tuple[float, ContributingFactor]:
        """
        Score based on job failure rate.
        >20% = High (100), 10-20% = Medium (60), <10% = Low (20)
        """
        if not signals:
            return 50.0, ContributingFactor(
                factor_name="Job Failure Rate",
                factor_value=0.0,
                weight=self.WEIGHTS["job_failure_rate"],
                impact="neutral",
                description="No job execution data available"
            )
        
        total_success = sum(s.job_success_count for s in signals)
        total_failure = sum(s.job_failure_count for s in signals)
        total_jobs = total_success + total_failure
        
        if total_jobs == 0:
            return 30.0, ContributingFactor(
                factor_name="Job Failure Rate",
                factor_value=0.0,
                weight=self.WEIGHTS["job_failure_rate"],
                impact="neutral",
                description="No jobs executed yet"
            )
        
        failure_rate = (total_failure / total_jobs) * 100
        
        if failure_rate > 20:
            score = 100.0
            impact = "negative"
            desc = f"High job failure rate: {failure_rate:.1f}% of jobs failing"
        elif failure_rate > 10:
            score = 60.0
            impact = "negative"
            desc = f"Moderate job failure rate: {failure_rate:.1f}% of jobs failing"
        else:
            score = 20.0
            impact = "positive"
            desc = f"Low job failure rate: {failure_rate:.1f}% of jobs failing"
        
        return score, ContributingFactor(
            factor_name="Job Failure Rate",
            factor_value=round(failure_rate, 2),
            weight=self.WEIGHTS["job_failure_rate"],
            impact=impact,
            description=desc
        )
    
    def _score_job_duration_trend(
        self, signals: List[PlatformSignal]
    ) -> Tuple[float, ContributingFactor]:
        """
        Score based on job duration trend.
        Increasing >30% = degrading (100), stable = (40), decreasing = (10)
        """
        if len(signals) < 2:
            return 40.0, ContributingFactor(
                factor_name="Job Duration Trend",
                factor_value=0.0,
                weight=self.WEIGHTS["job_duration_trend"],
                impact="neutral",
                description="Insufficient data for trend analysis"
            )
        
        # Sort by date and compare first half to second half
        sorted_signals = sorted(signals, key=lambda s: s.signal_date)
        mid = len(sorted_signals) // 2
        
        early_avg = sum(s.avg_job_duration_seconds for s in sorted_signals[:mid]) / mid
        late_avg = sum(s.avg_job_duration_seconds for s in sorted_signals[mid:]) / (len(sorted_signals) - mid)
        
        if early_avg == 0:
            change_pct = 0
        else:
            change_pct = ((late_avg - early_avg) / early_avg) * 100
        
        if change_pct > 30:
            score = 100.0
            impact = "negative"
            desc = f"Job durations increasing significantly: +{change_pct:.1f}%"
        elif change_pct > 0:
            score = 50.0
            impact = "neutral"
            desc = f"Job durations slightly increasing: +{change_pct:.1f}%"
        elif change_pct > -15:
            score = 30.0
            impact = "neutral"
            desc = f"Job durations stable: {change_pct:.1f}%"
        else:
            score = 10.0
            impact = "positive"
            desc = f"Job durations improving: {change_pct:.1f}%"
        
        return score, ContributingFactor(
            factor_name="Job Duration Trend",
            factor_value=round(change_pct, 2),
            weight=self.WEIGHTS["job_duration_trend"],
            impact=impact,
            description=desc
        )
    
    def _score_activity_recency(
        self, signals: List[PlatformSignal]
    ) -> Tuple[float, ContributingFactor]:
        """
        Score based on most recent platform activity.
        No activity >7 days = High (100), 3-7 days = Medium (50), <3 days = Low (10)
        """
        if not signals:
            return 80.0, ContributingFactor(
                factor_name="Activity Recency",
                factor_value=0.0,
                weight=self.WEIGHTS["activity_recency"],
                impact="negative",
                description="No platform activity recorded"
            )
        
        # Find most recent activity
        latest_activity = max(
            (s.last_activity_timestamp for s in signals if s.last_activity_timestamp),
            default=None
        )
        
        if not latest_activity:
            # Fall back to signal date
            latest_date = max(s.signal_date for s in signals)
            latest_activity = datetime.combine(latest_date, datetime.min.time())
        
        days_since = (datetime.utcnow() - latest_activity).days
        
        if days_since > 7:
            score = 100.0
            impact = "negative"
            desc = f"No platform activity in {days_since} days - potential stall"
        elif days_since > 3:
            score = 50.0
            impact = "neutral"
            desc = f"Limited recent activity - last seen {days_since} days ago"
        else:
            score = 10.0
            impact = "positive"
            desc = f"Active engagement - last activity {days_since} days ago"
        
        return score, ContributingFactor(
            factor_name="Activity Recency",
            factor_value=days_since,
            weight=self.WEIGHTS["activity_recency"],
            impact=impact,
            description=desc
        )
    
    def _score_sa_confidence(
        self, engagement: Engagement
    ) -> Tuple[float, ContributingFactor]:
        """
        Score based on SA self-reported confidence.
        1-2 = High risk (100), 3 = Medium (50), 4-5 = Low (10)
        """
        confidence = engagement.sa_confidence_score
        
        if confidence <= 2:
            score = 100.0
            impact = "negative"
            desc = f"SA confidence is low ({confidence}/5) - concerns flagged"
        elif confidence == 3:
            score = 50.0
            impact = "neutral"
            desc = f"SA confidence is moderate ({confidence}/5)"
        else:
            score = 10.0
            impact = "positive"
            desc = f"SA confidence is high ({confidence}/5) - delivery on track"
        
        return score, ContributingFactor(
            factor_name="SA Confidence",
            factor_value=confidence,
            weight=self.WEIGHTS["sa_confidence"],
            impact=impact,
            description=desc
        )
    
    def _score_schedule_variance(
        self, engagement: Engagement
    ) -> Tuple[float, ContributingFactor]:
        """
        Score based on schedule progress.
        >80% timeline consumed = High risk, 50-80% = Medium, <50% = Low
        """
        today = datetime.utcnow().date()
        start = engagement.start_date
        end = engagement.target_completion_date
        
        total_duration = (end - start).days
        elapsed = (today - start).days
        
        if total_duration <= 0:
            return 50.0, ContributingFactor(
                factor_name="Schedule Variance",
                factor_value=0.0,
                weight=self.WEIGHTS["schedule_variance"],
                impact="neutral",
                description="Invalid engagement dates"
            )
        
        progress_pct = (elapsed / total_duration) * 100
        
        if progress_pct > 100:
            score = 100.0
            impact = "negative"
            days_over = elapsed - total_duration
            desc = f"Engagement is {days_over} days past target completion"
        elif progress_pct > 80:
            score = 80.0
            impact = "negative"
            remaining = total_duration - elapsed
            desc = f"Approaching deadline: {remaining} days remaining ({progress_pct:.0f}% elapsed)"
        elif progress_pct > 50:
            score = 40.0
            impact = "neutral"
            remaining = total_duration - elapsed
            desc = f"Mid-engagement: {remaining} days remaining ({progress_pct:.0f}% elapsed)"
        else:
            score = 10.0
            impact = "positive"
            remaining = total_duration - elapsed
            desc = f"Early phase: {remaining} days remaining ({progress_pct:.0f}% elapsed)"
        
        return score, ContributingFactor(
            factor_name="Schedule Variance",
            factor_value=round(progress_pct, 2),
            weight=self.WEIGHTS["schedule_variance"],
            impact=impact,
            description=desc
        )
    
    def _determine_risk_level(self, score: float) -> RiskLevel:
        """Determine risk level from numeric score."""
        if score <= self.THRESHOLD_LOW:
            return RiskLevel.LOW
        elif score <= self.THRESHOLD_MEDIUM:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.HIGH
    
    def _determine_trend(
        self, current_score: float, previous_scores: List[RiskScore] = None
    ) -> TrendDirection:
        """Determine trend direction based on score history."""
        if not previous_scores or len(previous_scores) < 2:
            return TrendDirection.STABLE
        
        # Get average of last few scores
        recent_scores = sorted(previous_scores, key=lambda s: s.computed_at)[-3:]
        avg_previous = sum(s.risk_score for s in recent_scores) / len(recent_scores)
        
        diff = current_score - avg_previous
        
        if diff > 5:
            return TrendDirection.DEGRADING
        elif diff < -5:
            return TrendDirection.IMPROVING
        else:
            return TrendDirection.STABLE


# Singleton instance
_risk_engine = None


def get_risk_engine() -> RiskEngine:
    """Get the singleton risk engine instance."""
    global _risk_engine
    if _risk_engine is None:
        _risk_engine = RiskEngine()
    return _risk_engine
