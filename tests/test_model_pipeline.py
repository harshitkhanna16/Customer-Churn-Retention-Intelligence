"""Unit tests for ML models, artifacts, probabilities, and evaluation metrics."""

import pytest
import numpy as np
from src.models.registry import (
    load_best_model,
    load_evaluation_summary,
    load_model_metadata,
    load_preprocessor,
)
from src.utils.config import Config


def test_artifacts_exist():
    """Verify essential serialized artifacts exist on disk."""
    assert Config.BEST_MODEL_PATH.exists(), "Champion model file missing"
    assert Config.PREPROCESSOR_PATH.exists(), "Fitted preprocessor file missing"
    assert Config.MODEL_METADATA_PATH.exists(), "Model metadata file missing"
    assert Config.EVALUATION_SUMMARY_PATH.exists(), "Evaluation summary file missing"


def test_load_model_and_preprocessor():
    """Verify loading champion model and preprocessor."""
    model = load_best_model()
    preprocessor = load_preprocessor()

    assert hasattr(model, "predict_proba"), "Model must implement predict_proba"
    assert hasattr(preprocessor, "transform"), "Preprocessor must implement transform"


def test_evaluation_metrics_and_bounds():
    """Verify evaluation summary contains all required models and valid metric bounds."""
    eval_summary = load_evaluation_summary()

    required_models = ["Logistic_Regression", "Random_Forest", "XGBoost", "Dummy_Baseline"]
    for mod in required_models:
        assert mod in eval_summary, f"Model {mod} missing from evaluation summary"

        metrics = eval_summary[mod]["test_tuned_metrics"]
        assert 0.0 <= metrics["accuracy"] <= 1.0
        assert 0.0 <= metrics["precision"] <= 1.0
        assert 0.0 <= metrics["recall"] <= 1.0
        assert 0.0 <= metrics["f1"] <= 1.0
        assert 0.0 <= metrics["roc_auc"] <= 1.0
        assert 0.0 <= metrics["pr_auc"] <= 1.0

    # Ensure champion model meets quality threshold
    xgb_metrics = eval_summary["XGBoost"]["test_tuned_metrics"]
    assert xgb_metrics["roc_auc"] > 0.80, "Champion ROC-AUC must exceed 0.80"
    assert xgb_metrics["accuracy"] >= 0.80, "Champion Accuracy must exceed 0.80"
