"""Unit tests for dataset loading, schema verification, and validation."""

import pytest
import pandas as pd
from src.data.loader import get_data_filepath, load_raw_data
from src.data.validator import DataValidator, validate_batch_dataframe
from src.utils.config import Config


def test_get_data_filepath():
    """Verify raw dataset path resolution."""
    path = get_data_filepath()
    assert path.exists(), f"Dataset file does not exist at {path}"
    assert path.suffix == ".csv", "Dataset must be a CSV file"


def test_load_raw_data():
    """Verify raw dataset loading and schema."""
    df = load_raw_data()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 10000, f"Expected 10,000 rows, got {len(df)}"
    for col in Config.RAW_COLUMNS:
        assert col in df.columns, f"Expected column {col} missing from dataset"


def test_data_validator_report():
    """Verify comprehensive validation report generation."""
    df = load_raw_data()
    validator = DataValidator(df)
    report = validator.run_full_validation()

    assert report["summary"]["total_rows"] == 10000
    assert report["summary"]["total_columns"] == 14
    assert report["summary"]["total_missing_values"] == 0
    assert report["summary"]["duplicate_customer_ids"] == 0
    assert report["summary"]["is_clean"] is True
    assert "target_summary" in report
    assert abs(report["target_summary"]["churn_rate"] - 0.2037) < 0.001


def test_validate_batch_dataframe_valid():
    """Verify batch validation passes on clean feature DataFrame."""
    df = load_raw_data().head(10).drop(columns=["Exited"])
    is_valid, valid_df, invalid_df, errors = validate_batch_dataframe(df)

    assert is_valid is True
    assert len(valid_df) == 10
    assert len(invalid_df) == 0
    assert len(errors) == 0


def test_validate_batch_dataframe_invalid():
    """Verify batch validation catches corrupt categories and out of bound values."""
    bad_df = pd.DataFrame([
        {
            "CreditScore": 9999,  # out of bounds [300, 850]
            "Geography": "Atlantis",  # invalid category
            "Gender": "Unknown",  # invalid category
            "Age": 150,  # out of bounds
            "Tenure": 2,
            "Balance": 1000.0,
            "NumOfProducts": 1,
            "HasCrCard": 1,
            "IsActiveMember": 1,
            "EstimatedSalary": 50000.0,
        }
    ])
    is_valid, valid_df, invalid_df, errors = validate_batch_dataframe(bad_df)

    assert is_valid is False
    assert len(valid_df) == 0
    assert len(invalid_df) == 1
    assert "ValidationErrors" in invalid_df.columns
