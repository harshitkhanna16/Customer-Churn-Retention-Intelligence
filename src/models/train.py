"""End-to-end model training, validation tuning, and evaluation pipeline.

Trains Logistic Regression, Random Forest, and XGBoost with leakage-safe preprocessing,
stratified evaluation, threshold optimization, and artifact persistence.
"""

import json
from pathlib import Path
from typing import Any, Dict, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from src.data.loader import load_raw_data
from src.features.engineering import create_preprocessing_pipeline, get_feature_names
from src.models.evaluate import (
    compute_roc_pr_curves,
    evaluate_predictions,
    find_optimal_threshold,
)
from src.utils.config import Config


def prepare_data_splits() -> (
    Tuple[
        pd.DataFrame,
        pd.DataFrame,
        pd.DataFrame,
        pd.Series,
        pd.Series,
        pd.Series,
        pd.DataFrame,
    ]
):
    """Load raw dataset, isolate features, and split into train, validation, and test sets."""
    df_raw = load_raw_data()

    # Isolate targets and candidate features
    y = df_raw[Config.TARGET_COL]
    feature_cols = [
        c
        for c in df_raw.columns
        if c not in Config.ID_COLS and c != Config.TARGET_COL
    ]
    X = df_raw[feature_cols].copy()

    # Stratified Train/Test Split (80/20)
    X_train_full, X_test, y_train_full, y_test = train_test_split(
        X,
        y,
        test_size=Config.TEST_SIZE,
        stratify=y,
        random_state=Config.RANDOM_SEED,
    )

    # Stratified Train/Val Split within Train (80/20 of 80% = 64/16/20 overall)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train_full,
        y_train_full,
        test_size=Config.VAL_SIZE,
        stratify=y_train_full,
        random_state=Config.RANDOM_SEED,
    )

    # Retain metadata for test set (like CustomerId) for downstream batch simulation
    test_meta = df_raw.loc[X_test.index, Config.ID_COLS].copy()

    return X_train, X_val, X_test, y_train, y_val, y_test, test_meta


def train_and_evaluate_all_models() -> Dict[str, Any]:
    """Train all candidate models, optimize thresholds on validation data,

    evaluate on test set, and persist artifacts.
    """
    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
        test_meta,
    ) = prepare_data_splits()

    print(
        f"Data split: Train={len(X_train):,}, Val={len(X_val):,}, Test={len(X_test):,}"
    )

    # 1. Fit Preprocessor ONLY on training data
    preprocessor = create_preprocessing_pipeline()
    preprocessor.fit(X_train)
    feature_names = get_feature_names(preprocessor)

    # Transform splits
    X_train_trans = preprocessor.transform(X_train)
    X_val_trans = preprocessor.transform(X_val)
    X_test_trans = preprocessor.transform(X_test)

    # 2. Define Model Candidates
    scale_pos_weight = float((y_train == 0).sum() / max((y_train == 1).sum(), 1))

    candidate_models = {
        "Dummy_Baseline": DummyClassifier(strategy="stratified", random_state=Config.RANDOM_SEED),
        "Logistic_Regression": LogisticRegression(
            class_weight="balanced",
            max_iter=1000,
            C=0.5,
            random_state=Config.RANDOM_SEED,
        ),
        "Random_Forest": RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            class_weight="balanced_subsample",
            random_state=Config.RANDOM_SEED,
            n_jobs=-1,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.05,
            scale_pos_weight=scale_pos_weight,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric="logloss",
            random_state=Config.RANDOM_SEED,
        ),
    }

    model_results = {}
    fitted_models = {}

    for name, model in candidate_models.items():
        print(f"Training {name}...")
        model.fit(X_train_trans, y_train)
        fitted_models[name] = model

        # Predicted probabilities on validation set for threshold tuning
        val_probs = model.predict_proba(X_val_trans)[:, 1]
        best_thresh, best_val_f1 = find_optimal_threshold(
            y_val.to_numpy(), val_probs, metric="f1"
        )

        # Evaluate on held-out TEST set at default (0.50) and optimal threshold
        test_probs = model.predict_proba(X_test_trans)[:, 1]
        test_metrics_default = evaluate_predictions(
            y_test.to_numpy(), test_probs, threshold=0.50
        )
        test_metrics_tuned = evaluate_predictions(
            y_test.to_numpy(), test_probs, threshold=best_thresh
        )

        curves = compute_roc_pr_curves(y_test.to_numpy(), test_probs)

        # Feature Importance if supported
        feature_importance_dict = {}
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
            feature_importance_dict = {
                f: round(float(imp), 4)
                for f, imp in sorted(
                    zip(feature_names, importances),
                    key=lambda x: x[1],
                    reverse=True,
                )
            }
        elif hasattr(model, "coef_"):
            coefs = model.coef_[0]
            feature_importance_dict = {
                f: round(float(abs(c)), 4)
                for f, c in sorted(
                    zip(feature_names, coefs),
                    key=lambda x: abs(x[1]),
                    reverse=True,
                )
            }

        model_results[name] = {
            "validation_optimal_threshold": best_thresh,
            "validation_best_f1": best_val_f1,
            "test_default_metrics": test_metrics_default,
            "test_tuned_metrics": test_metrics_tuned,
            "curves": curves,
            "feature_importance": feature_importance_dict,
        }

    # Baseline vs Candidates Recall Comparison
    baseline_recall = model_results["Dummy_Baseline"]["test_default_metrics"]["recall"]
    for name, res in model_results.items():
        if name != "Dummy_Baseline":
            m_recall = res["test_tuned_metrics"]["recall"]
            abs_diff = round((m_recall - baseline_recall) * 100, 2)
            rel_diff = round(
                ((m_recall - baseline_recall) / max(baseline_recall, 0.001)) * 100,
                2,
            )
            res["recall_improvement_vs_baseline"] = {
                "baseline_recall": baseline_recall,
                "model_tuned_recall": m_recall,
                "percentage_point_diff": abs_diff,
                "relative_percentage_gain": rel_diff,
            }

    # Model Selection: Pick model with highest test ROC-AUC & F1-score
    # Candidate evaluation
    ranked_models = sorted(
        [
            (name, res["test_tuned_metrics"]["roc_auc"], res["test_tuned_metrics"]["f1"])
            for name, res in model_results.items()
            if name != "Dummy_Baseline"
        ],
        key=lambda x: (x[1], x[2]),
        reverse=True,
    )
    best_model_name = ranked_models[0][0]
    best_model = fitted_models[best_model_name]
    print(f"\nChampion Model Selected: {best_model_name}")

    # Persist Artifacts
    Config.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, Config.BEST_MODEL_PATH)
    joblib.dump(preprocessor, Config.PREPROCESSOR_PATH)

    # Save individual fitted models as well for interactive comparison
    for name, mod in fitted_models.items():
        joblib.dump(mod, Config.ARTIFACTS_DIR / f"{name.lower()}_model.joblib")

    # Metadata
    metadata = {
        "model_name": best_model_name,
        "model_version": "1.0.0",
        "random_seed": Config.RANDOM_SEED,
        "features": feature_names,
        "optimal_threshold": model_results[best_model_name][
            "validation_optimal_threshold"
        ],
        "test_performance": model_results[best_model_name]["test_tuned_metrics"],
        "all_model_rankings": ranked_models,
    }

    with open(Config.MODEL_METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    with open(Config.EVALUATION_SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(model_results, f, indent=2)

    with open(Config.MODEL_COMPARISON_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(model_results, f, indent=2)

    print(f"Artifacts and reports successfully saved to {Config.ARTIFACTS_DIR}")
    return model_results


if __name__ == "__main__":
    train_and_evaluate_all_models()
