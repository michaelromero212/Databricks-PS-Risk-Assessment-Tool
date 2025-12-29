"""
Data models and schemas for the Databricks PS Risk Assessment Tool.
Uses Pydantic for validation and serialization.
"""

from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid


# =============================================================================
# Enums
# =============================================================================

class ScopeSize(str, Enum):
    """Engagement scope size options."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class RiskLevel(str, Enum):
    """Risk level classifications."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TrendDirection(str, Enum):
    """Risk trend direction indicators."""
    IMPROVING = "improving"
    STABLE = "stable"
    DEGRADING = "degrading"


class AIGenerationStatus(str, Enum):
    """AI explanation generation status."""
    GENERATED = "generated_successfully"
    CACHED = "cached"
    UNAVAILABLE = "temporarily_unavailable"


class Industry(str, Enum):
    """Industry categories for engagements."""
    FINANCIAL_SERVICES = "Financial Services"
    HEALTHCARE = "Healthcare"
    TECHNOLOGY = "Technology"
    RETAIL = "Retail"
    MANUFACTURING = "Manufacturing"
    ENERGY = "Energy"
    MEDIA = "Media & Entertainment"
    PUBLIC_SECTOR = "Public Sector"
    OTHER = "Other"


# =============================================================================
# Engagement Models
# =============================================================================

class EngagementBase(BaseModel):
    """Base engagement model with common fields."""
    customer_name: str = Field(..., min_length=1, max_length=200)
    industry: Industry
    start_date: date
    target_completion_date: date
    scope_size: ScopeSize
    sa_assigned: str = Field(..., min_length=1, max_length=100)
    sa_confidence_score: int = Field(..., ge=1, le=5)


class EngagementCreate(EngagementBase):
    """Model for creating a new engagement."""
    pass


class Engagement(EngagementBase):
    """Complete engagement model with all fields."""
    engagement_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# =============================================================================
# Platform Signal Models
# =============================================================================

class PlatformSignalBase(BaseModel):
    """Base platform signal model."""
    engagement_id: str
    signal_date: date
    job_success_count: int = Field(default=0, ge=0)
    job_failure_count: int = Field(default=0, ge=0)
    avg_job_duration_seconds: float = Field(default=0.0, ge=0)
    notebook_execution_count: int = Field(default=0, ge=0)
    sql_query_count: int = Field(default=0, ge=0)
    last_activity_timestamp: Optional[datetime] = None


class PlatformSignalCreate(PlatformSignalBase):
    """Model for creating a new platform signal."""
    pass


class PlatformSignal(PlatformSignalBase):
    """Complete platform signal model."""
    signal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# =============================================================================
# Risk Score Models
# =============================================================================

class ContributingFactor(BaseModel):
    """A single contributing factor to risk score."""
    factor_name: str
    factor_value: float
    weight: float
    impact: str  # "positive", "negative", "neutral"
    description: str


class RiskScoreBase(BaseModel):
    """Base risk score model."""
    engagement_id: str
    risk_score: float = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    contributing_factors: List[ContributingFactor]
    trend_direction: TrendDirection


class RiskScoreCreate(RiskScoreBase):
    """Model for creating a new risk score."""
    pass


class RiskScore(RiskScoreBase):
    """Complete risk score model."""
    score_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    computed_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# =============================================================================
# AI Explanation Models
# =============================================================================

class AIExplanationBase(BaseModel):
    """Base AI explanation model."""
    engagement_id: str
    risk_explanation: str
    mitigation_suggestions: List[str]


class AIExplanationCreate(AIExplanationBase):
    """Model for creating a new AI explanation."""
    pass


class AIExplanation(AIExplanationBase):
    """Complete AI explanation model with metadata."""
    explanation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_name: str = "google/flan-t5-base"
    model_provider: str = "Hugging Face"
    model_purpose: str = "Risk explanation and recommendation generation"
    generation_status: AIGenerationStatus = AIGenerationStatus.GENERATED
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    cached: bool = False
    
    class Config:
        from_attributes = True


# =============================================================================
# Metrics Models
# =============================================================================

class MetricsBase(BaseModel):
    """Base metrics model."""
    metric_date: date
    active_engagement_count: int = Field(default=0, ge=0)
    high_risk_count: int = Field(default=0, ge=0)
    medium_risk_count: int = Field(default=0, ge=0)
    low_risk_count: int = Field(default=0, ge=0)
    avg_risk_score: float = Field(default=0.0, ge=0, le=100)
    ai_coverage_rate: float = Field(default=0.0, ge=0, le=100)


class MetricsCreate(MetricsBase):
    """Model for creating new metrics."""
    pass


class Metrics(MetricsBase):
    """Complete metrics model."""
    metric_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    computed_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


# =============================================================================
# Response Models
# =============================================================================

class EngagementWithRisk(Engagement):
    """Engagement with current risk information."""
    current_risk_score: Optional[float] = None
    current_risk_level: Optional[RiskLevel] = None
    trend_direction: Optional[TrendDirection] = None


class EngagementDetail(EngagementWithRisk):
    """Complete engagement detail with all related data."""
    signals: List[PlatformSignal] = []
    risk_history: List[RiskScore] = []
    ai_explanation: Optional[AIExplanation] = None


class HealthCheck(BaseModel):
    """API health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    databricks_connected: bool = False
    huggingface_available: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)
