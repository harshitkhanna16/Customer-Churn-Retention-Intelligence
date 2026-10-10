"""Configuration management for Customer Churn & Retention Intelligence.

Defines all filesystem paths, random seeds, schema definitions, model hyperparameter defaults,
and risk segmentation boundaries.
"""

from pathlib import Path
from typing import Dict, List, Tuple


class Config:
    """Central configuration class."""

    # Project Root Directory
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]

    # Data Paths
    DATA_DIR: Path = PROJECT_ROOT / "data"
    RAW_DATA_PATH: Path = DATA_DIR / "raw" / "Churn_Modelling.csv"
    FALLBACK_RAW_DATA_PATH: Path = PROJECT_ROOT / "Churn_Modelling.csv"
    PROCESSED_DATA_PATH: Path = DATA_DIR / "processed" / "churn_processed.csv"
    EXPORTS_DIR: Path = DATA_DIR / "exports"
    POWERBI_EXPORT_PATH: Path = EXPORTS_DIR / "powerbi_churn_dataset.csv"
    SAMPLE_BATCH_PATH: Path = EXPORTS_DIR / "sample_batch_customers.csv"

    # Database Path
    SQLITE_DB_PATH: Path = PROJECT_ROOT / "data" / "customer_churn.db"
    SQL_DIR: Path = PROJECT_ROOT / "sql"

    # Models and Artifacts Paths
    MODELS_DIR: Path = PROJECT_ROOT / "models"
    ARTIFACTS_DIR: Path = MODELS_DIR / "artifacts"
    BEST_MODEL_PATH: Path = ARTIFACTS_DIR / "best_model.joblib"
    PREPROCESSOR_PATH: Path = ARTIFACTS_DIR / "preprocessor.joblib"
    MODEL_METADATA_PATH: Path = ARTIFACTS_DIR / "model_metadata.json"
    EVALUATION_SUMMARY_PATH: Path = MODELS_DIR / "evaluation_summary.json"

    # Reports Paths
    REPORTS_DIR: Path = PROJECT_ROOT / "reports"
    DATA_QUALITY_REPORT_PATH: Path = REPORTS_DIR / "eda_data_quality_report.json"
    MODEL_COMPARISON_REPORT_PATH: Path = REPORTS_DIR / "model_comparison_report.json"

    # Random Seed
    RANDOM_SEED: int = 42

    # Schema Specifications
    TARGET_COL: str = "Exited"
    ID_COLS: List[str] = ["RowNumber", "CustomerId", "Surname"]

    RAW_COLUMNS: List[str] = [
        "RowNumber",
        "CustomerId",
        "Surname",
        "CreditScore",
        "Geography",
        "Gender",
        "Age",
        "Tenure",
        "Balance",
        "NumOfProducts",
        "HasCrCard",
        "IsActiveMember",
        "EstimatedSalary",
        "Exited",
    ]

    NUMERICAL_FEATURES: List[str] = [
        "CreditScore",
        "Age",
        "Tenure",
        "Balance",
        "NumOfProducts",
        "HasCrCard",
        "IsActiveMember",
        "EstimatedSalary",
    ]

    CATEGORICAL_FEATURES: List[str] = [
        "Geography",
        "Gender",
    ]

    EXPECTED_GEOGRAPHIES: List[str] = ["France", "Germany", "Spain"]
    EXPECTED_GENDERS: List[str] = ["Female", "Male"]

    # Model Evaluation and Split
    TEST_SIZE: float = 0.20
    VAL_SIZE: float = 0.20  # Fraction of train set for validation/tuning
    CV_FOLDS: int = 5

    # Default Probability Risk Thresholds
    DEFAULT_LOW_RISK_THRESHOLD: float = 0.35
    DEFAULT_HIGH_RISK_THRESHOLD: float = 0.65

    # Optimal Decision Threshold (Tuned on validation set to optimize F1 / recall)
    # Default initial fallback
    DEFAULT_DECISION_THRESHOLD: float = 0.40

    # Color Palette for Analytics & UI
    COLORS = {
        "primary": "#1E3A8A",      # Deep Navy
        "secondary": "#0284C7",    # Cerulean
        "accent": "#0D9488",       # Teal
        "background": "#0F172A",   # Slate Dark
        "card_bg": "#1E293B",      # Dark Slate Card
        "text": "#F8FAFC",         # Pure Off-White
        "retained": "#10B981",     # Emerald Green
        "churned": "#EF4444",      # Crimson Red
        "low_risk": "#10B981",     # Green
        "medium_risk": "#F59E0B",  # Amber
        "high_risk": "#EF4444",    # Red
    }
