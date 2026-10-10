"""Unit tests for individual and batch prediction scoring, risk tiers, and recommendations."""

import pytest
import pandas as pd
from src.predictions.scorer import (
    assign_risk_tier,
    generate_retention_recommendation,
    score_batch_customers,
    score_single_customer,
)


def test_assign_risk_tier():
    """Verify tier assignment boundary thresholds."""
    assert assign_risk_tier(0.10) == "Low Risk"
    assert assign_risk_tier(0.34) == "Low Risk"
    assert assign_risk_tier(0.35) == "Medium Risk"
    assert assign_risk_tier(0.50) == "Medium Risk"
    assert assign_risk_tier(0.64) == "Medium Risk"
    assert assign_risk_tier(0.65) == "High Risk"
    assert assign_risk_tier(0.95) == "High Risk"


def test_score_single_customer():
    """Verify single customer scoring output structure and value bounds."""
    sample = {
        "CreditScore": 650,
        "Geography": "Germany",
        "Gender": "Female",
        "Age": 45,
        "Tenure": 3,
        "Balance": 120000.0,
        "NumOfProducts": 1,
        "HasCrCard": 1,
        "IsActiveMember": 0,
        "EstimatedSalary": 80000.0,
    }

    res = score_single_customer(sample)
    assert "churn_probability" in res
    assert 0.0 <= res["churn_probability"] <= 1.0
    assert res["risk_tier"] in ["Low Risk", "Medium Risk", "High Risk"]
    assert "recommendation" in res
    assert "explanation" in res
    assert "primary_action" in res["recommendation"]


def test_score_batch_customers():
    """Verify batch scoring on a dataframe."""
    batch_records = pd.DataFrame([
        {
            "CreditScore": 600,
            "Geography": "France",
            "Gender": "Male",
            "Age": 30,
            "Tenure": 5,
            "Balance": 0.0,
            "NumOfProducts": 2,
            "HasCrCard": 1,
            "IsActiveMember": 1,
            "EstimatedSalary": 50000.0,
        },
        {
            "CreditScore": 700,
            "Geography": "Germany",
            "Gender": "Female",
            "Age": 55,
            "Tenure": 2,
            "Balance": 150000.0,
            "NumOfProducts": 1,
            "HasCrCard": 0,
            "IsActiveMember": 0,
            "EstimatedSalary": 100000.0,
        },
    ])

    scored = score_batch_customers(batch_records)
    assert len(scored) == 2
    assert "PredictedProbability" in scored.columns
    assert "RiskTier" in scored.columns
    assert "RecommendedAction" in scored.columns
    assert scored["PredictedProbability"].iloc[0] < scored["PredictedProbability"].iloc[1]
