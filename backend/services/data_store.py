"""
Demo data store for Databricks PS Risk Assessment Tool.
Provides in-memory storage with sample data for demonstration purposes.
In production, this would be replaced with Databricks Delta Lake queries.
"""

from datetime import date, datetime, timedelta
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import random
from backend.models.schemas import (
    Engagement,
    PlatformSignal,
    RiskScore,
    AIExplanation,
    Metrics,
    Industry,
    ScopeSize,
    RiskLevel,
    TrendDirection,
)
from backend.services.risk_engine import get_risk_engine
from backend.services.ai_explainer import get_ai_explainer


class DemoDataStore:
    """
    In-memory data store with demo data for the POC.
    Simulates Delta Lake table operations.
    """
    
    def __init__(self):
        """Initialize the data store with sample data."""
        self.engagements: Dict[str, Engagement] = {}
        self.signals: Dict[str, List[PlatformSignal]] = {}
        self.risk_scores: Dict[str, List[RiskScore]] = {}
        self.explanations: Dict[str, AIExplanation] = {}
        self.metrics: List[Metrics] = []
        
        # Usage tracking for PS Program Impact metrics
        self.usage_stats = {
            'assessments_generated': 5,  # Starting with initial demo count
            'ai_insights_delivered': 5,
            'time_saved_minutes': 75,   # 15 mins per assessment
            'active_users': 1
        }
        
        self._initialized = False
    
    def initialize(self):
        """Load demo data into the store."""
        if self._initialized:
            return
        
        self._create_sample_engagements()
        self._create_sample_signals()
        self._compute_risk_scores()
        self._generate_explanations()
        self._compute_metrics()
        
        self._initialized = True
    
    def _create_sample_engagements(self):
        """Create sample engagement data."""
        today = date.today()
        
        sample_engagements = [
            {
                "engagement_id": "eng-001",
                "customer_name": "Acme Financial Services",
                "industry": Industry.FINANCIAL_SERVICES,
                "start_date": today - timedelta(days=60),
                "target_completion_date": today + timedelta(days=30),
                "scope_size": ScopeSize.LARGE,
                "sa_assigned": "Sarah Chen",
                "sa_confidence_score": 2,
            },
            {
                "engagement_id": "eng-002",
                "customer_name": "TechCorp ML Platform",
                "industry": Industry.TECHNOLOGY,
                "start_date": today - timedelta(days=30),
                "target_completion_date": today + timedelta(days=60),
                "scope_size": ScopeSize.MEDIUM,
                "sa_assigned": "Marcus Johnson",
                "sa_confidence_score": 3,
            },
            {
                "engagement_id": "eng-003",
                "customer_name": "HealthFirst Analytics",
                "industry": Industry.HEALTHCARE,
                "start_date": today - timedelta(days=15),
                "target_completion_date": today + timedelta(days=75),
                "scope_size": ScopeSize.SMALL,
                "sa_assigned": "Emily Rodriguez",
                "sa_confidence_score": 5,
            },
            {
                "engagement_id": "eng-004",
                "customer_name": "RetailMax Data Lakehouse",
                "industry": Industry.RETAIL,
                "start_date": today - timedelta(days=45),
                "target_completion_date": today + timedelta(days=45),
                "scope_size": ScopeSize.LARGE,
                "sa_assigned": "David Kim",
                "sa_confidence_score": 3,
            },
            {
                "engagement_id": "eng-005",
                "customer_name": "EnergyGrid IoT Pipeline",
                "industry": Industry.ENERGY,
                "start_date": today - timedelta(days=75),
                "target_completion_date": today + timedelta(days=15),
                "scope_size": ScopeSize.MEDIUM,
                "sa_assigned": "Lisa Wang",
                "sa_confidence_score": 2,
            },
        ]
        
        for data in sample_engagements:
            engagement = Engagement(**data)
            self.engagements[engagement.engagement_id] = engagement
    
    def _create_sample_signals(self):
        """Create sample platform signals for each engagement."""
        today = date.today()
        
        # Signal profiles for different risk scenarios
        profiles = {
            "eng-001": {  # High risk - high failures, declining activity
                "failure_rate": 0.25,
                "duration_trend": 1.4,
                "activity_gap": 5,
            },
            "eng-002": {  # Medium risk - moderate issues
                "failure_rate": 0.12,
                "duration_trend": 1.1,
                "activity_gap": 2,
            },
            "eng-003": {  # Low risk - healthy metrics
                "failure_rate": 0.05,
                "duration_trend": 0.9,
                "activity_gap": 0,
            },
            "eng-004": {  # Medium risk - schedule pressure
                "failure_rate": 0.08,
                "duration_trend": 1.2,
                "activity_gap": 1,
            },
            "eng-005": {  # High risk - overdue, stalled
                "failure_rate": 0.30,
                "duration_trend": 1.5,
                "activity_gap": 8,
            },
        }
        
        for eng_id, profile in profiles.items():
            signals = []
            base_duration = 120.0  # seconds
            
            for i in range(14):  # 2 weeks of data
                signal_date = today - timedelta(days=13-i)
                
                # Calculate metrics based on profile
                total_jobs = random.randint(10, 30)
                failures = int(total_jobs * profile["failure_rate"] * random.uniform(0.7, 1.3))
                successes = total_jobs - failures
                
                # Duration increases over time for degrading engagements
                duration_factor = 1 + (i / 14) * (profile["duration_trend"] - 1)
                avg_duration = base_duration * duration_factor * random.uniform(0.9, 1.1)
                
                # Activity timestamp (with gaps for stalled engagements)
                if i >= 14 - profile["activity_gap"]:
                    last_activity = None
                else:
                    last_activity = datetime.combine(
                        signal_date,
                        datetime.min.time()
                    ) + timedelta(hours=random.randint(8, 18))
                
                signal = PlatformSignal(
                    engagement_id=eng_id,
                    signal_date=signal_date,
                    job_success_count=successes,
                    job_failure_count=failures,
                    avg_job_duration_seconds=round(avg_duration, 2),
                    notebook_execution_count=random.randint(5, 25),
                    sql_query_count=random.randint(20, 100),
                    last_activity_timestamp=last_activity
                )
                signals.append(signal)
            
            self.signals[eng_id] = signals
    
    def _compute_risk_scores(self):
        """Compute risk scores for all engagements."""
        engine = get_risk_engine()
        
        for eng_id, engagement in self.engagements.items():
            signals = self.signals.get(eng_id, [])
            previous_scores = self.risk_scores.get(eng_id, [])
            
            score = engine.compute_risk_score(engagement, signals, previous_scores)
            
            if eng_id not in self.risk_scores:
                self.risk_scores[eng_id] = []
            self.risk_scores[eng_id].append(score)
    
    def _generate_explanations(self):
        """Generate AI explanations for all engagements."""
        explainer = get_ai_explainer()
        
        for eng_id, engagement in self.engagements.items():
            scores = self.risk_scores.get(eng_id, [])
            if scores:
                latest_score = scores[-1]
                explanation = explainer.generate_explanation(
                    engagement,
                    latest_score,
                    use_cache=False
                )
                self.explanations[eng_id] = explanation
    
    def _compute_metrics(self):
        """Compute aggregate metrics."""
        today = date.today()
        
        active_count = len(self.engagements)
        
        # Count by risk level
        high_count = 0
        medium_count = 0
        low_count = 0
        total_score = 0.0
        
        for eng_id, scores in self.risk_scores.items():
            if scores:
                latest = scores[-1]
                total_score += latest.risk_score
                
                if latest.risk_level == RiskLevel.HIGH:
                    high_count += 1
                elif latest.risk_level == RiskLevel.MEDIUM:
                    medium_count += 1
                else:
                    low_count += 1
        
        avg_score = total_score / active_count if active_count > 0 else 0
        ai_coverage = (len(self.explanations) / active_count * 100) if active_count > 0 else 0
        
        metrics = Metrics(
            metric_date=today,
            active_engagement_count=active_count,
            high_risk_count=high_count,
            medium_risk_count=medium_count,
            low_risk_count=low_count,
            avg_risk_score=round(avg_score, 2),
            ai_coverage_rate=round(ai_coverage, 2)
        )
        
        self.metrics.append(metrics)
    
    # =========================================================================
    # Methods for adding new data (used by import feature)
    # =========================================================================
    
    def add_engagement(self, engagement: Engagement) -> None:
        """Add a new engagement to the store."""
        self.engagements[engagement.engagement_id] = engagement
    
    def add_signal(self, signal: PlatformSignal) -> None:
        """Add a platform signal for an engagement."""
        eng_id = signal.engagement_id
        if eng_id not in self.signals:
            self.signals[eng_id] = []
        self.signals[eng_id].append(signal)
    
    def add_risk_score(self, risk_score: RiskScore) -> None:
        """Add a risk score for an engagement."""
        eng_id = risk_score.engagement_id
        if eng_id not in self.risk_scores:
            self.risk_scores[eng_id] = []
        self.risk_scores[eng_id].append(risk_score)
    
    def add_explanation(self, explanation: AIExplanation) -> None:
        """Add an AI explanation for an engagement."""
        self.explanations[explanation.engagement_id] = explanation
    
    def refresh_metrics(self) -> None:
        """Recompute metrics after adding new data."""
        self._compute_metrics()
    
    # =========================================================================
    # Query methods
    # =========================================================================
    
    def get_all_engagements(self) -> List[Engagement]:
        """Get all engagements."""
        return list(self.engagements.values())
    
    def get_engagement(self, engagement_id: str) -> Optional[Engagement]:
        """Get a specific engagement by ID."""
        return self.engagements.get(engagement_id)
    
    def get_engagement_signals(self, engagement_id: str) -> List[PlatformSignal]:
        """Get signals for an engagement."""
        return self.signals.get(engagement_id, [])
    
    def get_latest_risk_score(self, engagement_id: str) -> Optional[RiskScore]:
        """Get the latest risk score for an engagement."""
        scores = self.risk_scores.get(engagement_id, [])
        return scores[-1] if scores else None
    
    def get_risk_history(self, engagement_id: str) -> List[RiskScore]:
        """Get risk score history for an engagement."""
        return self.risk_scores.get(engagement_id, [])
    
    def get_explanation(self, engagement_id: str) -> Optional[AIExplanation]:
        """Get the AI explanation for an engagement."""
        return self.explanations.get(engagement_id)
    
    def get_latest_metrics(self) -> Optional[Metrics]:
        """Get the most recent metrics."""
        return self.metrics[-1] if self.metrics else None
    
    def get_all_metrics(self) -> List[Metrics]:
        """Get all metrics history."""
        return self.metrics
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage stats for program impact metrics."""
        return self.usage_stats
    
    def _track_assessment(self, count: int = 1):
        """Track that an assessment has been performed."""
        self.usage_stats['assessments_generated'] += count
        self.usage_stats['ai_insights_delivered'] += count
        self.usage_stats['time_saved_minutes'] += (count * 15)  # 15 mins saved per review


# Singleton instance
_data_store = None


def get_data_store() -> DemoDataStore:
    """Get the singleton data store instance."""
    global _data_store
    if _data_store is None:
        _data_store = DemoDataStore()
        _data_store.initialize()
    return _data_store
