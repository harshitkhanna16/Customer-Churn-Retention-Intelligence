"""Prediction scoring engine, risk categorization, SHAP explainability, and retention logic.

Handles single-customer scoring, batch inference, threshold-based tiering,
feature contribution analysis, and prescriptive retention actions.
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import shap

from src.features.engineering import get_feature_names
from src.models.registry import load_best_model, load_preprocessor
from src.utils.config import Config


def assign_risk_tier(
    probability: float,
    low_threshold: float = Config.DEFAULT_LOW_RISK_THRESHOLD,
    high_threshold: float = Config.DEFAULT_HIGH_RISK_THRESHOLD,
) -> str:
    """Classify predicted probability into Low, Medium, or High Risk tier."""
    if probability < low_threshold:
        return "Low Risk"
    elif probability < high_threshold:
        return "Medium Risk"
    else:
        return "High Risk"


def generate_retention_recommendation(
    record: Dict[str, Any], probability: float, risk_tier: str
) -> Dict[str, Any]:
    """Prescribe rule-based retention strategies tailored to customer risk drivers.

    Note: Retention suggestions represent business heuristics, not causal guarantees.
    """
    actions: List[str] = []
    priority: str = "Standard"

    age = float(record.get("Age", 35))
    geo = str(record.get("Geography", "France"))
    num_products = int(record.get("NumOfProducts", 1))
    is_active = int(record.get("IsActiveMember", 1))
    balance = float(record.get("Balance", 0.0))

    if risk_tier == "High Risk":
        priority = "Urgent Intervention"
    elif risk_tier == "Medium Risk":
        priority = "Proactive Retention"
    else:
        priority = "Relationship Cadence"

    # Action 1: Product Count Driver
    if num_products == 1:
        actions.append(
            "Cross-Sell Second Core Product: Single-product customers show ~28% churn vs 7.6% for two-product holders. Introduce low-friction savings or debit rewards bundle."
        )
    elif num_products >= 3:
        actions.append(
            "Product Consolidation & Fee Audit: Multi-product holders (3+) exhibit acute dissatisfaction (~83%+ churn). Arrange dedicated relationship manager review to simplify terms."
        )

    # Action 2: Regional German Driver
    if geo == "Germany" and risk_tier in ["High Risk", "Medium Risk"]:
        actions.append(
            "Regional Branch Engagement: German accounts demonstrate 2x the national churn rate. Offer competitive deposit yield matching and in-person advisory consultation."
        )

    # Action 3: Inactivity Driver
    if is_active == 0:
        actions.append(
            "Digital Re-Activation Incentive: Inactive customers churn at 26.9%. Deploy personalized email and mobile push prompting high-yield goal setup or bill-pay activation."
        )

    # Action 4: Age Cohort Preservation
    if age >= 50 and balance > 50000:
        actions.append(
            "Senior Wealth Preservation Advisory: Mature high-balance demographic has high attrition exposure. Offer complimentary wealth planning and prioritized VIP support."
        )

    # Action 5: Low Risk Routine
    if not actions:
        actions.append(
            "Relationship Maintenance: Maintain standard communication cadence, deliver annual loyalty milestone rewards, and survey satisfaction quarterly."
        )

    return {
        "priority_level": priority,
        "primary_action": actions[0],
        "all_actions": actions,
        "disclaimer": (
            "Recommendation based on historical empirical churn patterns. "
            "Model estimates correlation, not causality; evaluate customer context before outreach."
        ),
    }


# Cache explainer in memory to avoid rebuilding on every call
_EXPLAINER_CACHE = None


def get_cached_explainer(model):
    """Retrieve or initialize SHAP TreeExplainer."""
    global _EXPLAINER_CACHE
    if _EXPLAINER_CACHE is None:
        try:
            _EXPLAINER_CACHE = shap.TreeExplainer(model)
        except Exception:
            _EXPLAINER_CACHE = None
    return _EXPLAINER_CACHE


def explain_prediction_shap(
    single_record_df: pd.DataFrame,
    model=None,
    preprocessor=None,
    top_n: int = 5,
) -> Dict[str, Any]:
    """Generate SHAP feature contributions for a single customer inference.

    Returns:
        Dictionary with base value, top risk-increasing drivers, top risk-decreasing drivers.
    """
    if model is None:
        model = load_best_model()
    if preprocessor is None:
        preprocessor = load_preprocessor()

    feature_names = get_feature_names(preprocessor)
    X_trans = preprocessor.transform(single_record_df)

    explainer = get_cached_explainer(model)
    if explainer is None:
        # Fallback if SHAP tree explainer fails
        return {
            "method": "Feature Importance Fallback",
            "top_positive": [],
            "top_negative": [],
            "base_value": 0.20,
            "disclaimer": "SHAP explanation unavailable for this configuration.",
        }

    try:
        shap_values = explainer.shap_values(X_trans)
        # For binary classification with XGBoost, shap_values might be array of shape (1, n_features)
        # or list of arrays
        if isinstance(shap_values, list):
            sv = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
        elif len(shap_values.shape) == 2:
            sv = shap_values[0]
        else:
            sv = shap_values

        base_val = (
            float(explainer.expected_value[1])
            if isinstance(explainer.expected_value, (list, np.ndarray))
            else float(explainer.expected_value)
        )

        # Pair features with values
        contributions = []
        for name, val in zip(feature_names, sv):
            contributions.append((name, float(val)))

        # Sort: positive pushes toward churn, negative pushes toward retention
        sorted_pos = sorted(
            [c for c in contributions if c[1] > 0], key=lambda x: x[1], reverse=True
        )[:top_n]
        sorted_neg = sorted(
            [c for c in contributions if c[1] < 0], key=lambda x: x[1]
        )[:top_n]

        return {
            "method": "SHAP TreeExplainer",
            "base_value": round(base_val, 4),
            "top_risk_drivers": [
                {"feature": f, "impact": round(imp, 4)} for f, imp in sorted_pos
            ],
            "top_retention_anchors": [
                {"feature": f, "impact": round(imp, 4)} for f, imp in sorted_neg
            ],
            "disclaimer": (
                "SHAP values quantify directional model feature attribution for this prediction. "
                "Attribution reflects learned statistical associations, not proved causality."
            ),
        }
    except Exception as exc:
        return {
            "method": f"Error: {exc}",
            "top_risk_drivers": [],
            "top_retention_anchors": [],
            "base_value": 0.20,
            "disclaimer": "Explanation could not be generated.",
        }


def score_single_customer(
    customer_dict: Dict[str, Any],
    low_thresh: float = Config.DEFAULT_LOW_RISK_THRESHOLD,
    high_thresh: float = Config.DEFAULT_HIGH_RISK_THRESHOLD,
    model=None,
    preprocessor=None,
) -> Dict[str, Any]:
    """Score an individual customer record and return comprehensive intelligence payload."""
    if model is None:
        model = load_best_model()
    if preprocessor is None:
        preprocessor = load_preprocessor()

    # Create 1-row DataFrame
    record_df = pd.DataFrame([customer_dict])

    # Transform and predict
    X_trans = preprocessor.transform(record_df)
    prob = float(model.predict_proba(X_trans)[0, 1])
    risk_tier = assign_risk_tier(prob, low_thresh, high_thresh)

    recommendation = generate_retention_recommendation(
        customer_dict, prob, risk_tier
    )
    explanation = explain_prediction_shap(
        record_df, model=model, preprocessor=preprocessor
    )

    return {
        "churn_probability": round(prob, 4),
        "churn_percentage": round(prob * 100, 2),
        "risk_tier": risk_tier,
        "recommendation": recommendation,
        "explanation": explanation,
    }


def score_batch_customers(
    batch_df: pd.DataFrame,
    low_thresh: float = Config.DEFAULT_LOW_RISK_THRESHOLD,
    high_thresh: float = Config.DEFAULT_HIGH_RISK_THRESHOLD,
    model=None,
    preprocessor=None,
) -> pd.DataFrame:
    """Score a DataFrame of customer records, appending predicted probabilities,

    risk tiers, and action items.
    """
    if model is None:
        model = load_best_model()
    if preprocessor is None:
        preprocessor = load_preprocessor()

    out_df = batch_df.copy()
    X_trans = preprocessor.transform(out_df)
    probabilities = model.predict_proba(X_trans)[:, 1]

    out_df["PredictedProbability"] = np.round(probabilities, 4)
    out_df["RiskTier"] = [
        assign_risk_tier(p, low_thresh, high_thresh) for p in probabilities
    ]
    out_df["RecommendedAction"] = [
        generate_retention_recommendation(row.to_dict(), p, tier)["primary_action"]
        for (_, row), p, tier in zip(
            out_df.iterrows(), probabilities, out_df["RiskTier"]
        )
    ]

    return out_df
