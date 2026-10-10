"""Unit tests for feature engineering transformations and preprocessing pipeline."""

import pytest
import numpy as np
import pandas as pd
from src.data.loader import load_raw_data
from src.features.engineering import (
    CustomerFeatureEngineer,
    create_preprocessing_pipeline,
    engineer_features_df,
    get_feature_names,
)


def test_engineer_features_df():
    """Verify engineered columns are created correctly with expected types."""
    df_raw = load_raw_data().head(100)
    df_eng = engineer_features_df(df_raw)

    expected_new_cols = [
        "AgeGroup",
        "TenureGroup",
        "BalanceSalaryRatio",
        "CreditScoreAgeRatio",
        "HasZeroBalance",
        "IsActive_x_NumOfProducts",
        "ProductsPerTenure",
    ]
    for col in expected_new_cols:
        assert col in df_eng.columns, f"Engineered column {col} was not created"

    assert df_eng["HasZeroBalance"].isin([0, 1]).all()
    assert (df_eng["BalanceSalaryRatio"] >= 0).all()
    assert (df_eng["CreditScoreAgeRatio"] > 0).all()


def test_preprocessing_pipeline_fit_transform():
    """Verify full Scikit-learn preprocessing pipeline executes without errors."""
    df_raw = load_raw_data().head(200)
    X = df_raw.drop(columns=["RowNumber", "CustomerId", "Surname", "Exited"])

    pipeline = create_preprocessing_pipeline()
    pipeline.fit(X)

    X_trans = pipeline.transform(X)
    assert isinstance(X_trans, np.ndarray)
    assert X_trans.shape[0] == 200
    assert X_trans.shape[1] > 10

    # Ensure no NaN or infinite values
    assert not np.isnan(X_trans).any(), "Transformed feature matrix contains NaNs"
    assert not np.isinf(X_trans).any(), "Transformed feature matrix contains Inf"

    # Verify feature names extraction
    names = get_feature_names(pipeline)
    assert len(names) == X_trans.shape[1]
