"""
AI Explainer Service for Databricks PS Risk Assessment Tool.
Uses Hugging Face models for generating risk explanations and mitigation suggestions.
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from backend.config import get_config
from backend.models.schemas import (
    RiskScore,
    Engagement,
    AIExplanation,
    AIGenerationStatus,
)


class AIExplainer:
    """
    AI-powered risk explanation generator using Hugging Face models.
    
    Features:
    - Deterministic prompting
    - Structured JSON output
    - Response caching
    - Graceful fallback when model unavailable
    """
    
    # Prompt template for risk explanation
    PROMPT_TEMPLATE = """Analyze this Databricks engagement risk profile and provide actionable insights:

Engagement: {customer_name}
Industry: {industry}
Scope: {scope_size}
Risk Level: {risk_level}
Risk Score: {risk_score}/100
Timeline: {timeline_status}

Contributing Factors:
{factors_text}

Based on this analysis, provide:
1. A plain-English explanation of why this engagement is at {risk_level} risk (2-3 sentences)
2. Top 3 specific, actionable mitigation steps the Solution Architect should take

Format your response as JSON with keys "explanation" and "mitigations" (array of strings)."""

    def __init__(self):
        """Initialize the AI explainer."""
        self._config = get_config()
        self._cache: Dict[str, AIExplanation] = {}
        self._model = None
        self._tokenizer = None
        self._model_loaded = False
    
    @property
    def model_name(self) -> str:
        """Get the model name."""
        return self._config.huggingface.model_name
    
    @property
    def model_provider(self) -> str:
        """Get the model provider."""
        return self._config.huggingface.model_provider
    
    @property
    def model_purpose(self) -> str:
        """Get the model purpose."""
        return self._config.huggingface.model_purpose
    
    def _load_model(self) -> bool:
        """
        Lazy load the Hugging Face model.
        Returns True if model loaded successfully.
        """
        if self._model_loaded:
            return True
        
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            
            print(f"Loading model: {self.model_name}")
            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            self._model_loaded = True
            print("Model loaded successfully")
            return True
        except Exception as e:
            print(f"Failed to load model: {e}")
            return False
    
    def _get_cache_key(self, engagement_id: str, risk_score: float) -> str:
        """Generate a cache key for an explanation."""
        data = f"{engagement_id}:{risk_score:.2f}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> Optional[AIExplanation]:
        """Check if we have a cached explanation."""
        return self._cache.get(cache_key)
    
    def _build_prompt(
        self, engagement: Engagement, risk_score: RiskScore
    ) -> str:
        """Build the prompt for the model."""
        # Format contributing factors
        factors_text = "\n".join([
            f"- {f.factor_name}: {f.description} (Impact: {f.impact})"
            for f in risk_score.contributing_factors
        ])
        
        # Calculate timeline status
        today = datetime.utcnow().date()
        start = engagement.start_date
        end = engagement.target_completion_date
        total_days = (end - start).days
        elapsed = (today - start).days
        remaining = total_days - elapsed
        
        if remaining < 0:
            timeline_status = f"OVERDUE by {abs(remaining)} days"
        else:
            timeline_status = f"{remaining} days remaining of {total_days} day engagement"
        
        return self.PROMPT_TEMPLATE.format(
            customer_name=engagement.customer_name,
            industry=engagement.industry.value,
            scope_size=engagement.scope_size.value,
            risk_level=risk_score.risk_level.value,
            risk_score=risk_score.risk_score,
            timeline_status=timeline_status,
            factors_text=factors_text
        )
    
    def _generate_with_model(self, prompt: str) -> Optional[Dict]:
        """Generate explanation using the loaded model."""
        if not self._load_model():
            return None
        
        try:
            # Tokenize input
            inputs = self._tokenizer(
                prompt,
                return_tensors="pt",
                max_length=512,
                truncation=True
            )
            
            # Generate response
            outputs = self._model.generate(
                inputs.input_ids,
                max_length=300,
                num_beams=4,
                early_stopping=True,
                do_sample=False  # Deterministic
            )
            
            # Decode response
            response = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Try to parse as JSON
            try:
                result = json.loads(response)
                if "explanation" in result and "mitigations" in result:
                    return result
            except json.JSONDecodeError:
                pass
            
            # If not valid JSON, structure the response
            return {
                "explanation": response,
                "mitigations": [
                    "Review engagement timeline and milestone progress",
                    "Schedule sync with customer stakeholders",
                    "Assess technical blockers with engineering team"
                ]
            }
            
        except Exception as e:
            print(f"Model generation failed: {e}")
            return None
    
    def _generate_fallback(
        self, engagement: Engagement, risk_score: RiskScore
    ) -> Dict:
        """Generate a rule-based fallback explanation."""
        level = risk_score.risk_level.value
        score = risk_score.risk_score
        
        # Build explanation based on contributing factors
        negative_factors = [
            f for f in risk_score.contributing_factors
            if f.impact == "negative"
        ]
        
        if negative_factors:
            factor_summary = ", ".join([f.factor_name.lower() for f in negative_factors[:2]])
            explanation = (
                f"This {engagement.customer_name} engagement is at {level} risk "
                f"(score: {score}/100) primarily due to {factor_summary}. "
                f"The {engagement.scope_size.value} scope {engagement.industry.value} "
                f"project requires attention to prevent delivery delays."
            )
        else:
            explanation = (
                f"The {engagement.customer_name} engagement is currently at {level} risk "
                f"with an overall score of {score}/100. "
                f"The engagement metrics are within acceptable parameters."
            )
        
        # Generate mitigations based on negative factors
        mitigations = []
        for factor in negative_factors[:3]:
            if "failure" in factor.factor_name.lower():
                mitigations.append(
                    "Investigate job failures and implement error handling improvements"
                )
            elif "duration" in factor.factor_name.lower():
                mitigations.append(
                    "Review job performance and optimize long-running processes"
                )
            elif "activity" in factor.factor_name.lower():
                mitigations.append(
                    "Re-engage with customer team to resume platform utilization"
                )
            elif "confidence" in factor.factor_name.lower():
                mitigations.append(
                    "Schedule SA debrief to address concerns and realign expectations"
                )
            elif "schedule" in factor.factor_name.lower():
                mitigations.append(
                    "Reassess timeline feasibility and discuss scope adjustments with customer"
                )
        
        # Add default mitigations if needed
        default_mitigations = [
            "Schedule a checkpoint meeting with customer stakeholders",
            "Review and update the project plan with realistic milestones",
            "Document technical blockers and escalation paths"
        ]
        
        while len(mitigations) < 3:
            for m in default_mitigations:
                if m not in mitigations:
                    mitigations.append(m)
                    break
        
        return {
            "explanation": explanation,
            "mitigations": mitigations[:3]
        }
    
    def generate_explanation(
        self,
        engagement: Engagement,
        risk_score: RiskScore,
        use_cache: bool = True
    ) -> AIExplanation:
        """
        Generate an AI-powered explanation for an engagement's risk.
        
        Args:
            engagement: The engagement to explain
            risk_score: The computed risk score
            use_cache: Whether to use cached explanations
            
        Returns:
            AIExplanation with explanation text and mitigation suggestions
        """
        cache_key = self._get_cache_key(
            engagement.engagement_id,
            risk_score.risk_score
        )
        
        # Check cache first
        if use_cache:
            cached = self._check_cache(cache_key)
            if cached:
                cached.cached = True
                cached.generation_status = AIGenerationStatus.CACHED
                return cached
        
        # Build the prompt
        prompt = self._build_prompt(engagement, risk_score)
        
        # Try to generate with the model
        result = self._generate_with_model(prompt)
        
        if result:
            status = AIGenerationStatus.GENERATED
        else:
            # Fall back to rule-based generation
            result = self._generate_fallback(engagement, risk_score)
            status = AIGenerationStatus.UNAVAILABLE
        
        # Create the explanation object
        explanation = AIExplanation(
            engagement_id=engagement.engagement_id,
            risk_explanation=result["explanation"],
            mitigation_suggestions=result["mitigations"],
            model_name=self.model_name,
            model_provider=self.model_provider,
            model_purpose=self.model_purpose,
            generation_status=status,
            cached=False
        )
        
        # Cache the result
        self._cache[cache_key] = explanation
        
        return explanation
    
    def get_model_status(self) -> Dict:
        """Get the current status of the AI model."""
        return {
            "model_name": self.model_name,
            "model_provider": self.model_provider,
            "model_purpose": self.model_purpose,
            "model_loaded": self._model_loaded,
            "cache_size": len(self._cache),
            "available": True  # Always available due to fallback
        }
    
    def clear_cache(self):
        """Clear the explanation cache."""
        self._cache.clear()


# Singleton instance
_ai_explainer = None


def get_ai_explainer() -> AIExplainer:
    """Get the singleton AI explainer instance."""
    global _ai_explainer
    if _ai_explainer is None:
        _ai_explainer = AIExplainer()
    return _ai_explainer
