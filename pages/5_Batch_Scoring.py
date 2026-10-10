"""Page 5: Batch Customer Scoring & Schema Validation."""

import io
import pandas as pd
import plotly.express as px
import streamlit as st

from src.data.validator import validate_batch_dataframe
from src.predictions.scorer import score_batch_customers
from src.utils.config import Config
from src.utils.ui import (
    apply_custom_styles,
    get_plotly_layout,
    render_kpi_card,
)

st.set_page_config(page_title="Batch Scoring", page_icon="📁", layout="wide")
apply_custom_styles()

st.title("📁 Batch Customer Scoring & Risk Management")
st.markdown(
    "<p class='page-subtitle'>Bulk CSV Ingestion, Schema Validation, Live Inference, and Scored Data Export</p>",
    unsafe_allow_html=True,
)

# Template Download
col_info, col_download = st.columns([3, 1])
with col_info:
    st.markdown(
        "Upload a CSV containing new or unlabelled customer records. The engine validates column presence, "
        "numerical ranges, and categorical constraints before scoring."
    )
with col_download:
    if Config.SAMPLE_BATCH_PATH.exists():
        with open(Config.SAMPLE_BATCH_PATH, "rb") as f:
            sample_bytes = f.read()
        st.download_button(
            "📥 Download Sample CSV Template",
            data=sample_bytes,
            file_name="sample_batch_customers.csv",
            mime="text/csv",
            use_container_width=True,
        )

uploaded_file = st.file_uploader(
    "Choose a customer batch CSV file", type=["csv"], help="Upload CSV containing required customer features"
)

# Use sample template as default if no file uploaded
if uploaded_file is None:
    st.info("ℹ️ No file uploaded. You can click 'Load Demo 50-Customer Batch' below to test the batch scoring pipeline instantly.")
    if st.button("🚀 Load Demo 50-Customer Batch"):
        uploaded_df = pd.read_csv(Config.SAMPLE_BATCH_PATH)
    else:
        st.stop()
else:
    try:
        uploaded_df = pd.read_csv(uploaded_file)
    except Exception as exc:
        st.error(f"Failed to read CSV: {exc}")
        st.stop()

st.subheader(f"1. Ingested Records ({len(uploaded_df):,} Customers)")
st.dataframe(uploaded_df.head(5), use_container_width=True)

# Validation Phase
is_valid, valid_df, invalid_df, error_msgs = validate_batch_dataframe(uploaded_df)

if not is_valid:
    st.error("⚠️ Validation issues detected in uploaded batch:")
    for msg in error_msgs:
        st.write(f"- {msg}")
    if not invalid_df.empty:
        st.markdown("#### Invalid Rows Inspection")
        st.dataframe(invalid_df[["ValidationErrors"] + [c for c in invalid_df.columns if c != "ValidationErrors"]].head(10))
    if valid_df.empty:
        st.error("No valid rows could be scored. Please correct errors and re-upload.")
        st.stop()
    else:
        st.warning(f"Proceeding to score {len(valid_df):,} valid records out of {len(uploaded_df):,}.")
else:
    st.success(f"✅ Schema & Domain Boundary Validation Passed for all {len(uploaded_df):,} records!")

# Scoring Phase
with st.spinner("Scoring customer risk probabilities..."):
    scored_df = score_batch_customers(valid_df)

st.markdown("---")
st.subheader("2. Batch Scoring Intelligence Summary")

total_scored = len(scored_df)
high_count = int((scored_df["RiskTier"] == "High Risk").sum())
med_count = int((scored_df["RiskTier"] == "Medium Risk").sum())
low_count = int((scored_df["RiskTier"] == "Low Risk").sum())
avg_risk_prob = float(scored_df["PredictedProbability"].mean()) * 100

b1, b2, b3, b4 = st.columns(4)
with b1:
    render_kpi_card("Total Scored", f"{total_scored:,}", "Records processed")
with b2:
    render_kpi_card("High Risk Flagged", f"{high_count:,}", f"{high_count/total_scored*100:.1f}% urgent priority")
with b3:
    render_kpi_card("Medium Risk Flagged", f"{med_count:,}", f"{med_count/total_scored*100:.1f}% watch list")
with b4:
    render_kpi_card("Avg Churn Probability", f"{avg_risk_prob:.1f}%", f"{low_count:,} in Low Risk tier")

# Filter and Inspect
st.markdown("---")
st.subheader("3. Filterable Customer Scoring Table")

f_col1, f_col2 = st.columns(2)
with f_col1:
    tier_filter = st.multiselect(
        "Filter by Risk Tier:",
        options=["High Risk", "Medium Risk", "Low Risk"],
        default=["High Risk", "Medium Risk", "Low Risk"],
    )
with f_col2:
    geo_filter = st.multiselect(
        "Filter by Geography:",
        options=scored_df["Geography"].unique().tolist(),
        default=scored_df["Geography"].unique().tolist(),
    )

display_df = scored_df[
    (scored_df["RiskTier"].isin(tier_filter)) & (scored_df["Geography"].isin(geo_filter))
].sort_values(by="PredictedProbability", ascending=False)

st.dataframe(
    display_df[[
        "CustomerId" if "CustomerId" in display_df.columns else "CreditScore",
        "Geography",
        "Age",
        "Balance",
        "NumOfProducts",
        "PredictedProbability",
        "RiskTier",
        "RecommendedAction",
    ]],
    use_container_width=True,
    hide_index=True,
)

# Export Scored CSV
csv_buffer = io.StringIO()
display_df.to_csv(csv_buffer, index=False)
st.download_button(
    "📥 Download Scored Batch Predictions (CSV)",
    data=csv_buffer.getvalue(),
    file_name="batch_scored_predictions.csv",
    mime="text/csv",
    use_container_width=True,
)
