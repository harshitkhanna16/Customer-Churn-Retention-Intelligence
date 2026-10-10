"""Model artifact registry and deserialization manager.

Provides safe functions to retrieve trained models, preprocessors,
and performance reports with informative error handling.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional
import joblib

from src.utils.config import Config


def load_best_model():
    """Load the trained champion model from disk."""
    if not Config.BEST_MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model not found at {Config.BEST_MODEL_PATH}. "
            f"Please run model training pipeline first: python -m src.models.train"
        )
    return joblib.load(Config.BEST_MODEL_PATH)


def load_preprocessor():
    """Load the fitted Scikit-learn preprocessing pipeline."""
    if not Config.PREPROCESSOR_PATH.exists():
        raise FileNotFoundError(
            f"Preprocessor not found at {Config.PREPROCESSOR_PATH}. "
            f"Please run model training pipeline first: python -m src.models.train"
        )
    return joblib.load(Config.PREPROCESSOR_PATH)


def load_candidate_model(model_name: str):
    """Load a specific candidate model (e.g. 'xgboost', 'random_forest', 'logistic_regression')."""
    target = Config.ARTIFACTS_DIR / f"{model_name.lower()}_model.joblib"
    if not target.exists():
        raise FileNotFoundError(f"Model artifact not found for {model_name} at {target}")
    return joblib.load(target)


def load_model_metadata() -> Dict[str, Any]:
    """Load serialized model metadata and feature descriptions."""
    if not Config.MODEL_METADATA_PATH.exists():
        return {}
    with open(Config.MODEL_METADATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_evaluation_summary() -> Dict[str, Any]:
    """Load model evaluation comparison summary."""
    if not Config.EVALUATION_SUMMARY_PATH.exists():
        return {}
    with open(Config.EVALUATION_SUMMARY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
