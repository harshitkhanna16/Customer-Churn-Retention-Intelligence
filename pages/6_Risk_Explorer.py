"""Page 6: Customer Risk Explorer & Segmentation Matrix."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.predictions.scorer import assign_risk_tier
from src.utils.config import Config
from src.utils.ui import (
    apply_custom_styles,
    get_plotly_layout,
    render_kpi_card,
)

st.set_page_config(page_title="Customer Risk Explorer", page_icon="🧭", layout="wide")
apply_custom_styles()

st.title("🧭 Customer Risk Explorer")
st.markdown(
    "<p class='page-subtitle'>Configurable Risk Tiers, Portfolio Segmentation, and High-Risk Priority Queue</p>",
    unsafe_allow_html=True,
)

if not Config.POWERBI_EXPORT_PATH.exists():
    st.error("Pre-scored portfolio dataset not found. Please run: `python -m src.models.train`")
    st.stop()

df_scored = pd.read_csv(Config.POWERBI_EXPORT_PATH)

# Configurable Threshold Controls
st.sidebar.header("⚙️ Risk Threshold Tuning")
low_thresh = st.sidebar.slider(
    "Low / Medium Risk Boundary",
    min_value=0.15,
    max_value=0.50,
    value=0.35,
    step=0.05,
    help="Probabilities below this threshold are classified as Low Risk.",
)
high_thresh = st.sidebar.slider(
    "Medium / High Risk Boundary",
    min_value=0.50,
    max_value=0.85,
    value=0.65,
    step=0.05,
    help="Probabilities at or above this threshold are classified as High Risk.",
)

# Recompute Tiers Dynamically based on configured slider thresholds
df_scored["DynamicRiskTier"] = [
    assign_risk_tier(p, low_thresh, high_thresh) for p in df_scored["PredictedProbability"]
]

total_cust = len(df_scored)
high_df = df_scored[df_scored["DynamicRiskTier"] == "High Risk"]
med_df = df_scored[df_scored["DynamicRiskTier"] == "Medium Risk"]
low_df = df_scored[df_scored["DynamicRiskTier"] == "Low Risk"]

high_exposure = float(high_df["Balance"].sum())
total_exposure = float(df_scored["Balance"].sum())

# 1. Top Cards
r1, r2, r3, r4 = st.columns(4)
with r1:
    render_kpi_card("High Risk Tier", f"{len(high_df):,}", f"{len(high_df)/total_cust*100:.1f}% of portfolio")
with r2:
    render_kpi_card("Medium Risk Tier", f"{len(med_df):,}", f"{len(med_df)/total_cust*100:.1f}% under surveillance")
with r3:
    render_kpi_card("Low Risk Tier", f"{len(low_df):,}", f"{len(low_df)/total_cust*100:.1f}% stable relationship")
with r4:
    render_kpi_card("High Risk Deposits", f"${high_exposure/1e6:.2f}M", f"{high_exposure/total_exposure*100:.1f}% of total balances")

st.markdown("---")

# 2. Risk Matrix & Geography Breakdown
col_mat1, col_mat2 = st.columns(2)

with col_mat1:
    tier_counts = pd.DataFrame({
        "RiskTier": ["Low Risk", "Medium Risk", "High Risk"],
        "Count": [len(low_df), len(med_df), len(high_df)],
        "Balance": [low_df["Balance"].sum(), med_df["Balance"].sum(), high_df["Balance"].sum()],
    })
    fig_donut = px.pie(
        tier_counts,
        values="Count",
        names="RiskTier",
        hole=0.45,
        title="Portfolio Share by Configured Risk Tier",
        color="RiskTier",
        color_discrete_map={"Low Risk": "#10B981", "Medium Risk": "#F59E0B", "High Risk": "#EF4444"},
    )
    fig_donut.update_layout(get_plotly_layout("Portfolio Share by Risk Tier"))
    st.plotly_chart(fig_donut, use_container_width=True)

with col_mat2:
    geo_risk = (
        df_scored.groupby(["Geography", "DynamicRiskTier"], observed=False)
        .size()
        .reset_index(name="CustomerCount")
    )
    fig_geo_risk = px.bar(
        geo_risk,
        x="Geography",
        y="CustomerCount",
        color="DynamicRiskTier",
        barmode="group",
        title="Risk Segmentation Across Geographies",
        color_discrete_map={"Low Risk": "#10B981", "Medium Risk": "#F59E0B", "High Risk": "#EF4444"},
    )
    fig_geo_risk.update_layout(get_plotly_layout("Risk Segmentation Across Geographies"))
    st.plotly_chart(fig_geo_risk, use_container_width=True)

st.markdown("---")

# 3. High-Risk Customer Prioritization Queue
st.subheader("3. High-Risk Priority Action Queue")

search_id = st.text_input("🔍 Search by Customer ID:", placeholder="Enter 8-digit Customer ID (e.g., 15634602)")

filtered_queue = high_df.copy()
if search_id.strip():
    try:
        cid_int = int(search_id.strip())
        filtered_queue = df_scored[df_scored["CustomerId"] == cid_int]
    except ValueError:
        st.warning("Please enter a valid numeric Customer ID.")

st.dataframe(
    filtered_queue[[
        "CustomerId",
        "Surname",
        "Geography",
        "Age",
        "NumOfProducts",
        "Balance",
        "PredictedProbability",
        "DynamicRiskTier",
        "RecommendedAction",
    ]].sort_values(by="PredictedProbability", ascending=False).head(100),
    use_container_width=True,
    hide_index=True,
)
