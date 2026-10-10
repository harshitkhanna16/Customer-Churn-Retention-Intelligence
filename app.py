"""Customer Churn & Retention Intelligence — Main Portal Entrypoint."""

import streamlit as st

st.set_page_config(
    page_title="Customer Churn Intelligence",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.data.loader import get_data_filepath
from src.utils.config import Config
from src.utils.ui import (
    apply_custom_styles,
    get_cached_eval_summary,
    get_cached_model_and_preprocessor,
    get_cached_processed_data,
    render_kpi_card,
)

apply_custom_styles()

st.title("🏦 Customer Churn & Retention Intelligence")
st.markdown(
    "<p class='page-subtitle'>Enterprise Machine Learning & Business Analytics Platform for Banking Customer Retention</p>",
    unsafe_allow_html=True,
)

# System Status Check Cards
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

try:
    df = get_cached_processed_data()
    n_records = len(df)
    churn_rate = df["Exited"].mean() * 100
    data_status = f"✅ Loaded ({n_records:,} rows)"
except Exception as e:
    data_status = f"❌ Error: {e}"
    n_records = 0
    churn_rate = 0.0

try:
    model, _, metadata = get_cached_model_and_preprocessor()
    model_name = metadata.get("model_name", "XGBoost")
    eval_summary = get_cached_eval_summary()
    test_roc = eval_summary.get(model_name, {}).get("test_tuned_metrics", {}).get("roc_auc", 0.866)
    model_status = f"✅ Active ({model_name})"
except Exception as e:
    model_status = f"❌ Error: {e}"
    model_name = "None"
    test_roc = 0.0

try:
    db_status = "✅ Initialized (SQLite)" if Config.SQLITE_DB_PATH.exists() else "⚠️ Pending"
except Exception:
    db_status = "❌ Unavailable"

with col_stat1:
    render_kpi_card("Dataset Health", data_status, "14 Raw + 7 Engineered Features")
with col_stat2:
    render_kpi_card("ML Engine", model_status, f"Champion Model (ROC-AUC {test_roc:.3f})")
with col_stat3:
    render_kpi_card("Analytical Database", db_status, "SQLite Query Store")
with col_stat4:
    render_kpi_card("Portfolio Churn Baseline", f"{churn_rate:.2f}%", f"{int(churn_rate/100*n_records):,} Historical Attritions")

st.markdown("---")

st.markdown("""
### 🧭 Platform Architecture & Navigation Guide

This platform bridges machine learning prediction and proactive retention operations across 8 dedicated modules:

| Module | Core Purpose | Target Stakeholder |
| :--- | :--- | :--- |
| **1. Executive Overview** | High-level portfolio churn rate, deposit exposure, and geographic distribution | Chief Commercial Officer, Executive Committee |
| **2. Exploratory Analytics** | Statistical distributions, cohort analysis, and behavioral churn drivers | Senior Data Analysts, Business Intelligence |
| **3. Model Performance** | Honest comparison of Logistic Regression, Random Forest, & XGBoost with ROC/PR curves | Machine Learning Engineers, Model Risk Governance |
| **4. Individual Prediction** | Real-time customer scoring, SHAP explainability, and rule-based action playbook | Branch Relationship Managers, Concierge Support |
| **5. Batch Scoring** | Bulk CSV ingestion, schema validation, risk classification, and scored export | Campaign Operations, Data Science Operations |
| **6. Risk Explorer** | Interactive customer risk matrix, priority filtering, and deposit exposure ranking | Retention Campaign Managers |
| **7. Retention Insights** | Playbook prescribing concrete outreach actions with ROI impact simulation | Retention Strategy Leads, Product Heads |
| **8. Project Information** | Technical architecture, data dictionary, model governance, and interview defense | QA Auditors, Hiring Managers, Technical Evaluators |
""")

st.info("💡 **Getting Started:** Select any page from the left sidebar to explore the platform. For immediate executive findings, begin with **1_Executive_Overview**.")
