"""Exploratory Data Analysis and statistical aggregation utilities.

Computes univariate metrics, segment-level churn rates, correlation matrices,
and financial exposure breakdowns directly from loaded data.
"""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from src.utils.config import Config


def generate_dataset_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate high-level dataset statistics."""
    total_customers = len(df)
    target_col = Config.TARGET_COL

    churned_customers = int(df[target_col].sum()) if target_col in df.columns else 0
    retained_customers = total_customers - churned_customers
    churn_rate = (churned_customers / total_customers) if total_customers > 0 else 0.0
    retention_rate = 1.0 - churn_rate

    total_balance = float(df["Balance"].sum())
    churned_balance = (
        float(df[df[target_col] == 1]["Balance"].sum())
        if target_col in df.columns
        else 0.0
    )
    churned_balance_share = (
        (churned_balance / total_balance) if total_balance > 0 else 0.0
    )

    return {
        "total_customers": total_customers,
        "churned_customers": churned_customers,
        "retained_customers": retained_customers,
        "churn_rate": churn_rate,
        "retention_rate": retention_rate,
        "total_balance": total_balance,
        "churned_balance": churned_balance,
        "churned_balance_share": churned_balance_share,
        "avg_credit_score": float(df["CreditScore"].mean()),
        "avg_age": float(df["Age"].mean()),
        "avg_balance": float(df["Balance"].mean()),
        "avg_salary": float(df["EstimatedSalary"].mean()),
    }


def calculate_segment_churn(
    df: pd.DataFrame, group_col: str, target_col: str = Config.TARGET_COL
) -> pd.DataFrame:
    """Calculate empirical churn rate and volume metrics for a specific feature.

    Args:
        df: Input DataFrame.
        group_col: Column to group by.
        target_col: Target binary column (default: 'Exited').

    Returns:
        DataFrame containing segment breakdown.
    """
    if group_col not in df.columns or target_col not in df.columns:
        return pd.DataFrame()

    agg_df = (
        df.groupby(group_col, observed=False)[target_col]
        .agg(
            TotalCustomers="count",
            ChurnedCustomers="sum",
            RetainedCustomers=lambda x: (x == 0).sum(),
            ChurnRate="mean",
        )
        .reset_index()
    )

    agg_df["RetentionRate"] = 1.0 - agg_df["ChurnRate"]
    agg_df["CustomerShare"] = agg_df["TotalCustomers"] / len(df)

    # Add total balance per segment if Balance column exists
    if "Balance" in df.columns:
        balance_agg = (
            df.groupby(group_col, observed=False)["Balance"]
            .agg(TotalSegmentBalance="sum", AvgSegmentBalance="mean")
            .reset_index()
        )
        agg_df = pd.merge(agg_df, balance_agg, on=group_col, how="left")

    return agg_df.sort_values(by="TotalCustomers", ascending=False)


def calculate_financial_exposure(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate financial metrics distinguishing total deposits from churned exposure.

    Note: Account balance represents customer deposits held by the bank,
    not revenue or bank income.
    """
    target = Config.TARGET_COL
    if target not in df.columns:
        return {}

    churned_mask = df[target] == 1
    retained_mask = df[target] == 0

    total_deposits = float(df["Balance"].sum())
    churned_deposits = float(df.loc[churned_mask, "Balance"].sum())
    retained_deposits = float(df.loc[retained_mask, "Balance"].sum())

    avg_balance_churned = float(df.loc[churned_mask, "Balance"].mean())
    avg_balance_retained = float(df.loc[retained_mask, "Balance"].mean())

    # Deposits by geography
    geo_exposure = (
        df.groupby("Geography")
        .apply(
            lambda g: pd.Series(
                {
                    "TotalDeposits": g["Balance"].sum(),
                    "ChurnedDeposits": g.loc[g[target] == 1, "Balance"].sum(),
                    "SegmentChurnRate": g[target].mean(),
                }
            )
        )
        .reset_index()
        .to_dict(orient="records")
    )

    return {
        "total_deposits": total_deposits,
        "churned_deposits": churned_deposits,
        "retained_deposits": retained_deposits,
        "churned_deposits_share": (
            churned_deposits / total_deposits if total_deposits > 0 else 0.0
        ),
        "avg_balance_churned": avg_balance_churned,
        "avg_balance_retained": avg_balance_retained,
        "geography_breakdown": geo_exposure,
    }


def calculate_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate Pearson correlation matrix for numerical features and target."""
    numerical_cols = [
        "CreditScore",
        "Age",
        "Tenure",
        "Balance",
        "NumOfProducts",
        "HasCrCard",
        "IsActiveMember",
        "EstimatedSalary",
    ]
    if Config.TARGET_COL in df.columns:
        numerical_cols.append(Config.TARGET_COL)

    present_cols = [c for c in numerical_cols if c in df.columns]
    return df[present_cols].corr().round(3)
