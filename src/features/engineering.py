"""Feature engineering and preprocessing pipeline for Customer Churn Intelligence.

Provides reproducible, leakage-safe transformations compliant with Scikit-learn standards.
"""

from typing import List, Tuple
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.utils.config import Config


def engineer_features_df(df: pd.DataFrame) -> pd.DataFrame:
    """Create domain-justified business features on a customer DataFrame.

    Features created:
    - AgeGroup: Generational cohort (<30, 30-40, 40-50, 50-60, 60+)
    - TenureGroup: Relationship duration (0-2y, 3-5y, 6-8y, 9-10y)
    - BalanceSalaryRatio: Balance divided by (EstimatedSalary + 1)
    - CreditScoreAgeRatio: CreditScore divided by Age
    - HasZeroBalance: Binary flag indicating zero balance
    - IsActive_x_NumOfProducts: Engagement interaction term
    - ProductsPerTenure: Product density per year of tenure

    Args:
        df: Input DataFrame containing raw customer features.

    Returns:
        DataFrame with added engineered columns.
    """
    out = df.copy()

    # 1. Age Cohort Bins
    age_bins = [17, 30, 40, 50, 60, 120]
    age_labels = ["<30", "30-40", "40-50", "50-60", "60+"]
    out["AgeGroup"] = pd.cut(
        out["Age"], bins=age_bins, labels=age_labels, right=True
    ).astype(str)

    # 2. Tenure Cohort Bins
    tenure_bins = [-1, 2, 5, 8, 12]
    tenure_labels = ["0-2y", "3-5y", "6-8y", "9-10y"]
    out["TenureGroup"] = pd.cut(
        out["Tenure"], bins=tenure_bins, labels=tenure_labels, right=True
    ).astype(str)

    # 3. Financial Ratios
    out["BalanceSalaryRatio"] = out["Balance"] / (out["EstimatedSalary"] + 1.0)
    out["CreditScoreAgeRatio"] = out["CreditScore"] / out["Age"].clip(lower=18)

    # 4. Zero Balance Flag
    out["HasZeroBalance"] = (out["Balance"] == 0.0).astype(int)

    # 5. Product & Engagement Interactions
    out["IsActive_x_NumOfProducts"] = out["IsActiveMember"] * out["NumOfProducts"]
    out["ProductsPerTenure"] = out["NumOfProducts"] / (out["Tenure"] + 1.0)

    return out


class CustomerFeatureEngineer(BaseEstimator, TransformerMixin):
    """Scikit-learn compatible transformer that applies feature engineering."""

    def __init__(self):
        pass

    def fit(self, X: pd.DataFrame, y=None):
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)
        return engineer_features_df(X)


def create_preprocessing_pipeline() -> Pipeline:
    """Create a leakage-safe Scikit-learn preprocessing pipeline.

    Includes:
    - Custom Feature Engineering
    - ColumnTransformer with:
        - StandardScaler for numerical & ratio features
        - OneHotEncoder for categorical features (Geography, Gender, AgeGroup, TenureGroup)

    Returns:
        Fitted or unfitted Pipeline ready for model integration.
    """
    numerical_cols = [
        "CreditScore",
        "Age",
        "Tenure",
        "Balance",
        "NumOfProducts",
        "HasCrCard",
        "IsActiveMember",
        "EstimatedSalary",
        "BalanceSalaryRatio",
        "CreditScoreAgeRatio",
        "HasZeroBalance",
        "IsActive_x_NumOfProducts",
        "ProductsPerTenure",
    ]

    categorical_cols = [
        "Geography",
        "Gender",
        "AgeGroup",
        "TenureGroup",
    ]

    col_transformer = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numerical_cols),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                categorical_cols,
            ),
        ],
        remainder="drop",
    )

    full_preprocessor = Pipeline(
        steps=[
            ("engineer", CustomerFeatureEngineer()),
            ("col_transform", col_transformer),
        ]
    )

    return full_preprocessor


def get_feature_names(pipeline: Pipeline) -> List[str]:
    """Extract human-readable feature names from a fitted preprocessing pipeline."""
    col_transform: ColumnTransformer = pipeline.named_steps["col_transform"]
    feature_names = []

    for name, trans, cols in col_transform.transformers_:
        if name == "num":
            feature_names.extend(cols)
        elif name == "cat":
            if hasattr(trans, "get_feature_names_out"):
                cat_names = list(trans.get_feature_names_out(cols))
            else:
                cat_names = [f"cat_{c}" for c in cols]
            feature_names.extend(cat_names)

    return feature_names
