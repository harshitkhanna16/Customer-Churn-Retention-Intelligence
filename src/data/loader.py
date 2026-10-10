"""Data loading and persistence utilities.

Provides secure functions to discover, load, and persist datasets
with schema checks and error handling.
"""

import os
from pathlib import Path
from typing import Optional
import pandas as pd

from src.utils.config import Config


def get_data_filepath() -> Path:
    """Resolve the location of Churn_Modelling.csv across configured locations.

    Returns:
        Path to the raw CSV file.

    Raises:
        FileNotFoundError: If the dataset is not found in expected locations.
    """
    if Config.RAW_DATA_PATH.exists():
        return Config.RAW_DATA_PATH
    if Config.FALLBACK_RAW_DATA_PATH.exists():
        return Config.FALLBACK_RAW_DATA_PATH

    raise FileNotFoundError(
        f"Bank Customer Churn dataset not found. Expected locations:\n"
        f"1. {Config.RAW_DATA_PATH}\n"
        f"2. {Config.FALLBACK_RAW_DATA_PATH}\n"
        f"Please place Churn_Modelling.csv in data/raw/ or the project root."
    )


def load_raw_data(filepath: Optional[Path] = None) -> pd.DataFrame:
    """Load the raw churn dataset into a pandas DataFrame.

    Args:
        filepath: Optional custom path to dataset CSV.

    Returns:
        pd.DataFrame containing the raw records.

    Raises:
        ValueError: If essential columns are missing or file is corrupted.
    """
    target_path = filepath if filepath is not None else get_data_filepath()

    try:
        df = pd.read_csv(target_path)
    except Exception as exc:
        raise ValueError(f"Failed to read CSV from {target_path}: {exc}") from exc

    # Validate presence of expected columns
    missing_cols = [c for c in Config.RAW_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Dataset at {target_path} is missing expected columns: {missing_cols}"
        )

    return df


def save_processed_data(df: pd.DataFrame, output_path: Optional[Path] = None) -> Path:
    """Save cleaned and feature-engineered dataset to disk.

    Args:
        df: Processed DataFrame.
        output_path: Optional path to save to; defaults to Config.PROCESSED_DATA_PATH.

    Returns:
        Path where file was saved.
    """
    dest = output_path if output_path is not None else Config.PROCESSED_DATA_PATH
    dest.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dest, index=False)
    return dest
