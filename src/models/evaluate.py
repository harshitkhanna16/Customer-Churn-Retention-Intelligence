"""Model evaluation metrics and business cost-benefit utilities.

Calculates comprehensive classification metrics, ROC/PR curves, confusion matrices,
and threshold optimization without data leakage.
"""

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    auc,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


def evaluate_predictions(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.50,
) -> Dict[str, Any]:
    """Calculate classification metrics for binary churn predictions.

    Args:
        y_true: Ground truth binary labels.
        y_prob: Predicted churn probabilities.
        threshold: Decision cutoff threshold.

    Returns:
        Dictionary of comprehensive performance metrics.
    """
    y_pred = (y_prob >= threshold).astype(int)

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    roc_auc = float(roc_auc_score(y_true, y_prob))

    # Precision-Recall AUC
    p_curve, r_curve, _ = precision_recall_curve(y_true, y_prob)
    pr_auc = float(auc(r_curve, p_curve))

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    # Business rates
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

    return {
        "threshold": float(threshold),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "confusion_matrix": {
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
        },
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
    }


def find_optimal_threshold(
    y_val: np.ndarray,
    y_prob_val: np.ndarray,
    metric: str = "f1",
) -> Tuple[float, float]:
    """Find the optimal probability threshold on validation data.

    Args:
        y_val: Validation ground truth labels.
        y_prob_val: Validation predicted probabilities.
        metric: Metric to optimize ('f1', 'balanced_accuracy', 'recall').

    Returns:
        (best_threshold, best_score)
    """
    thresholds = np.linspace(0.10, 0.90, 81)
    best_thresh = 0.50
    best_score = -1.0

    for t in thresholds:
        preds = (y_prob_val >= t).astype(int)
        if metric == "f1":
            score = f1_score(y_val, preds, zero_division=0)
        elif metric == "recall":
            score = recall_score(y_val, preds, zero_division=0)
        else:
            score = accuracy_score(y_val, preds)

        if score > best_score:
            best_score = score
            best_thresh = float(t)

    return round(best_thresh, 3), round(float(best_score), 4)


def compute_roc_pr_curves(
    y_true: np.ndarray, y_prob: np.ndarray
) -> Dict[str, Any]:
    """Compute curve data suitable for interactive Plotly charts."""
    fpr, tpr, roc_thresh = roc_curve(y_true, y_prob)
    precision, recall, pr_thresh = precision_recall_curve(y_true, y_prob)

    return {
        "roc": {
            "fpr": fpr.round(4).tolist(),
            "tpr": tpr.round(4).tolist(),
            "thresholds": roc_thresh.round(4).tolist(),
            "auc": round(float(roc_auc_score(y_true, y_prob)), 4),
        },
        "pr": {
            "precision": precision.round(4).tolist(),
            "recall": recall.round(4).tolist(),
            "thresholds": pr_thresh.round(4).tolist(),
            "auc": round(float(auc(recall, precision)), 4),
        },
    }
