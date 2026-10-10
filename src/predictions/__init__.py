"""Predictions package initialization."""
from .scorer import (
    assign_risk_tier,
    explain_prediction_shap,
    generate_retention_recommendation,
    score_batch_customers,
    score_single_customer,
)

__all__ = [
    "assign_risk_tier",
    "explain_prediction_shap",
    "generate_retention_recommendation",
    "score_batch_customers",
    "score_single_customer",
]
