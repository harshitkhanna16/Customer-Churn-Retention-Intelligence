"""Analytics and EDA package."""
from .eda import (
    calculate_correlation_matrix,
    calculate_financial_exposure,
    calculate_segment_churn,
    generate_dataset_summary,
)

__all__ = [
    "calculate_correlation_matrix",
    "calculate_financial_exposure",
    "calculate_segment_churn",
    "generate_dataset_summary",
]
