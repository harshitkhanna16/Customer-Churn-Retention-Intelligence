"""Data validation and quality reporting module.

Performs schema verification, data type assertions, domain-range validation,
duplicate checks, and generates exportable data quality reports.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.utils.config import Config


class DataValidator:
    """Validator for Bank Customer Churn datasets."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.report: Dict[str, Any] = {}

    def run_full_validation(self) -> Dict[str, Any]:
        """Execute full validation suite and produce a comprehensive report."""
        n_rows, n_cols = self.df.shape

        # 1. Null values check
        null_counts = self.df.isnull().sum().to_dict()
        total_nulls = int(sum(null_counts.values()))

        # 2. Duplicate checks
        id_col = "CustomerId" if "CustomerId" in self.df.columns else None
        duplicate_ids = (
            int(self.df[id_col].duplicated().sum()) if id_col else 0
        )
        total_duplicate_rows = int(self.df.duplicated().sum())

        # 3. Categorical distribution & anomalies
        cat_anomalies = {}
        if "Geography" in self.df.columns:
            invalid_geo = self.df[
                ~self.df["Geography"].isin(Config.EXPECTED_GEOGRAPHIES)
            ]
            cat_anomalies["Geography"] = {
                "invalid_count": int(len(invalid_geo)),
                "observed_values": self.df["Geography"].value_counts().to_dict(),
            }
        if "Gender" in self.df.columns:
            invalid_gender = self.df[~self.df["Gender"].isin(Config.EXPECTED_GENDERS)]
            cat_anomalies["Gender"] = {
                "invalid_count": int(len(invalid_gender)),
                "observed_values": self.df["Gender"].value_counts().to_dict(),
            }

        # 4. Numerical range boundaries checks
        boundary_checks = {}
        num_rules = {
            "CreditScore": (300, 850),
            "Age": (18, 100),
            "Tenure": (0, 10),
            "Balance": (0.0, 1_000_000.0),
            "NumOfProducts": (1, 4),
            "HasCrCard": (0, 1),
            "IsActiveMember": (0, 1),
            "EstimatedSalary": (0.0, 10_000_000.0),
        }

        for col, (low, high) in num_rules.items():
            if col in self.df.columns:
                series = pd.to_numeric(self.df[col], errors="coerce")
                out_of_bounds = series[(series < low) | (series > high)]
                boundary_checks[col] = {
                    "min_observed": float(series.min()) if not series.empty else None,
                    "max_observed": float(series.max()) if not series.empty else None,
                    "expected_range": [low, high],
                    "out_of_bounds_count": int(len(out_of_bounds)),
                }

        # 5. Outlier Detection via IQR (for continuous features)
        outlier_summary = {}
        for col in ["CreditScore", "Age", "Balance", "EstimatedSalary"]:
            if col in self.df.columns:
                q1 = float(self.df[col].quantile(0.25))
                q3 = float(self.df[col].quantile(0.75))
                iqr = q3 - q1
                lower_fence = q1 - 1.5 * iqr
                upper_fence = q3 + 1.5 * iqr
                outliers = self.df[(self.df[col] < lower_fence) | (self.df[col] > upper_fence)]
                outlier_summary[col] = {
                    "q1": q1,
                    "q3": q3,
                    "iqr": iqr,
                    "lower_fence": lower_fence,
                    "upper_fence": upper_fence,
                    "outlier_count": int(len(outliers)),
                    "outlier_pct": round(float(len(outliers) / n_rows * 100), 2),
                }

        # 6. Target distribution check
        target_summary = {}
        if Config.TARGET_COL in self.df.columns:
            counts = self.df[Config.TARGET_COL].value_counts().to_dict()
            total_target = len(self.df)
            target_summary = {
                "counts": {str(k): int(v) for k, v in counts.items()},
                "churn_rate": float(self.df[Config.TARGET_COL].mean()),
                "retention_rate": float(1.0 - self.df[Config.TARGET_COL].mean()),
                "imbalance_ratio": round(
                    float(counts.get(0, 1) / max(counts.get(1, 1), 1)), 2
                ),
            }

        self.report = {
            "summary": {
                "total_rows": n_rows,
                "total_columns": n_cols,
                "total_missing_values": total_nulls,
                "duplicate_customer_ids": duplicate_ids,
                "duplicate_rows": total_duplicate_rows,
                "is_clean": total_nulls == 0 and duplicate_ids == 0,
            },
            "null_counts": null_counts,
            "categorical_checks": cat_anomalies,
            "boundary_checks": boundary_checks,
            "outlier_summary": outlier_summary,
            "target_summary": target_summary,
        }
        return self.report

    def save_report(self, output_path: Optional[Path] = None) -> Path:
        """Export the validation report as JSON."""
        dest = (
            output_path
            if output_path is not None
            else Config.DATA_QUALITY_REPORT_PATH
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not self.report:
            self.run_full_validation()
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(self.report, f, indent=2)
        return dest


def validate_batch_dataframe(
    df: pd.DataFrame,
) -> Tuple[bool, pd.DataFrame, pd.DataFrame, List[str]]:
    """Validate a batch dataframe provided for inference.

    Allows records without the 'Exited' column.
    Checks column presence, type coercibility, and domain boundaries.

    Returns:
        (is_valid, valid_df, invalid_df, error_messages)
    """
    required_features = (
        Config.NUMERICAL_FEATURES + Config.CATEGORICAL_FEATURES
    )
    missing_cols = [c for c in required_features if c not in df.columns]
    if missing_cols:
        return (
            False,
            pd.DataFrame(),
            df,
            [f"Batch file is missing required columns: {missing_cols}"],
        )

    errors_per_row: Dict[int, List[str]] = {idx: [] for idx in df.index}

    # Check categories
    for idx, geo in df["Geography"].items():
        if str(geo).strip() not in Config.EXPECTED_GEOGRAPHIES:
            errors_per_row[idx].append(
                f"Invalid Geography '{geo}'. Allowed: {Config.EXPECTED_GEOGRAPHIES}"
            )

    for idx, gender in df["Gender"].items():
        if str(gender).strip() not in Config.EXPECTED_GENDERS:
            errors_per_row[idx].append(
                f"Invalid Gender '{gender}'. Allowed: {Config.EXPECTED_GENDERS}"
            )

    # Check numerical bounds
    bounds = {
        "CreditScore": (300, 850),
        "Age": (18, 100),
        "Tenure": (0, 10),
        "Balance": (0.0, 1_000_000.0),
        "NumOfProducts": (1, 4),
        "HasCrCard": (0, 1),
        "IsActiveMember": (0, 1),
        "EstimatedSalary": (0.0, 10_000_000.0),
    }

    for col, (low, high) in bounds.items():
        for idx, val in df[col].items():
            try:
                num_val = float(val)
                if np.isnan(num_val) or num_val < low or num_val > high:
                    errors_per_row[idx].append(
                        f"{col} value {val} out of bounds [{low}, {high}]"
                    )
            except (ValueError, TypeError):
                errors_per_row[idx].append(
                    f"{col} value '{val}' could not be parsed as a number"
                )

    invalid_indices = [
        idx for idx, errs in errors_per_row.items() if len(errs) > 0
    ]
    valid_indices = [
        idx for idx, errs in errors_per_row.items() if len(errs) == 0
    ]

    valid_df = df.loc[valid_indices].copy()
    invalid_df = df.loc[invalid_indices].copy()

    if not invalid_df.empty:
        invalid_df["ValidationErrors"] = [
            "; ".join(errors_per_row[idx]) for idx in invalid_indices
        ]

    global_errors = []
    if invalid_indices:
        global_errors.append(
            f"Found {len(invalid_indices)} rows with validation errors out of {len(df)} total rows."
        )

    is_all_valid = len(invalid_indices) == 0
    return is_all_valid, valid_df, invalid_df, global_errors
