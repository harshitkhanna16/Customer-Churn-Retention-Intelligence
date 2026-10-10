"""Page 1: Executive Overview Dashboard."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analytics.eda import generate_dataset_summary
from src.utils.config import Config
from src.utils.ui import (
    apply_custom_styles,
    get_cached_processed_data,
    get_plotly_layout,
    render_kpi_card,
)

st.set_page_config(page_title="Executive Overview", page_icon="📊", layout="wide")
apply_custom_styles()

st.title("📊 Executive Overview")
st.markdown(
    "<p class='page-subtitle'>Portfolio-Level Attrition Metrics, Deposit Exposure, and Segment Distributions</p>",
    unsafe_allow_html=True,
)

df = get_cached_processed_data()

# Sidebar Filters
st.sidebar.header("🔍 Executive Slicers")
selected_geo = st.sidebar.multiselect(
    "Geography",
    options=df["Geography"].unique().tolist(),
    default=df["Geography"].unique().tolist(),
)
selected_gender = st.sidebar.multiselect(
    "Gender",
    options=df["Gender"].unique().tolist(),
    default=df["Gender"].unique().tolist(),
)
selected_products = st.sidebar.multiselect(
    "Number of Products",
    options=sorted(df["NumOfProducts"].unique().tolist()),
    default=sorted(df["NumOfProducts"].unique().tolist()),
)

# Filter Data
filtered_df = df[
    (df["Geography"].isin(selected_geo))
    & (df["Gender"].isin(selected_gender))
    & (df["NumOfProducts"].isin(selected_products))
]

if filtered_df.empty:
    st.warning("⚠️ No customer records match the selected filter combination.")
    st.stop()

# Calculations
total_cust = len(filtered_df)
churned_cust = int(filtered_df["Exited"].sum())
retained_cust = total_cust - churned_cust
churn_rate = (churned_cust / total_cust) * 100 if total_cust > 0 else 0.0
retention_rate = 100.0 - churn_rate

total_balance = float(filtered_df["Balance"].sum())
churned_balance = float(filtered_df.loc[filtered_df["Exited"] == 1, "Balance"].sum())
churned_balance_share = (
    (churned_balance / total_balance * 100) if total_balance > 0 else 0.0
)

# Load Power BI export if available to pull pre-scored predicted high-risk metrics
high_risk_count = 0
if Config.POWERBI_EXPORT_PATH.exists():
    pbi_df = pd.read_csv(Config.POWERBI_EXPORT_PATH)
    filtered_pbi = pbi_df[pbi_df["CustomerId"].isin(filtered_df["CustomerId"])]
    high_risk_count = int((filtered_pbi["RiskTier"] == "High Risk").sum())
high_risk_pct = (high_risk_count / total_cust * 100) if total_cust > 0 else 0.0

# 1. Top KPI Cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Total Customers", f"{total_cust:,}", f"{total_cust/len(df)*100:.1f}% of total portfolio")
with c2:
    render_kpi_card(
        "Historical Churn Rate",
        f"{churn_rate:.2f}%",
        f"{churned_cust:,} churned vs {retained_cust:,} retained",
    )
with c3:
    render_kpi_card(
        "Predicted High-Risk Customers",
        f"{high_risk_count:,}",
        f"{high_risk_pct:.1f}% assigned High Risk (ML model)",
    )
with c4:
    render_kpi_card(
        "Customer Deposits Held",
        f"${total_balance/1e6:.2f}M",
        f"${churned_balance/1e6:.2f}M historical attrition ({churned_balance_share:.1f}%)",
    )

st.caption(
    "📌 **Financial Metric Disclosure:** Account Balance represents customer deposits held by the institution, not bank revenue or fee income. Churn reflects historical closed accounts."
)

st.markdown("---")

# 2. Charts Section
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    geo_agg = (
        filtered_df.groupby("Geography", observed=False)["Exited"]
        .agg(Total="count", Churned="sum", ChurnRate="mean")
        .reset_index()
    )
    geo_agg["ChurnRatePct"] = geo_agg["ChurnRate"] * 100
    fig_geo = px.bar(
        geo_agg,
        x="Geography",
        y="ChurnRatePct",
        text=geo_agg["ChurnRatePct"].apply(lambda v: f"{v:.1f}%"),
        color="Geography",
        color_discrete_map={"France": "#0284C7", "Germany": "#EF4444", "Spain": "#10B981"},
        title="Historical Churn Rate by Geography",
        labels={"ChurnRatePct": "Churn Rate (%)"},
    )
    fig_geo.update_layout(get_plotly_layout("Historical Churn Rate by Geography"), showlegend=False)
    st.plotly_chart(fig_geo, use_container_width=True)

with row1_col2:
    age_agg = (
        filtered_df.groupby("AgeGroup", observed=False)["Exited"]
        .agg(Total="count", Churned="sum", ChurnRate="mean")
        .reset_index()
    )
    age_agg["ChurnRatePct"] = age_agg["ChurnRate"] * 100
    fig_age = px.line(
        age_agg,
        x="AgeGroup",
        y="ChurnRatePct",
        markers=True,
        title="Churn Rate Across Age Cohorts",
        labels={"ChurnRatePct": "Churn Rate (%)", "AgeGroup": "Age Cohort"},
    )
    fig_age.update_traces(line_color="#F59E0B", line_width=3, marker=dict(size=9, color="#EF4444"))
    fig_age.update_layout(get_plotly_layout("Churn Rate Across Age Cohorts"))
    st.plotly_chart(fig_age, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    prod_agg = (
        filtered_df.groupby("NumOfProducts", observed=False)["Exited"]
        .agg(Total="count", Churned="sum", ChurnRate="mean")
        .reset_index()
    )
    prod_agg["ChurnRatePct"] = prod_agg["ChurnRate"] * 100
    fig_prod = px.bar(
        prod_agg,
        x="NumOfProducts",
        y="ChurnRatePct",
        text=prod_agg["ChurnRatePct"].apply(lambda v: f"{v:.1f}%"),
        title="Churn Rate by Number of Products Held",
        labels={"ChurnRatePct": "Churn Rate (%)", "NumOfProducts": "Product Count"},
        color="NumOfProducts",
        color_continuous_scale="Reds",
    )
    fig_prod.update_layout(get_plotly_layout("Churn Rate by Number of Products Held"), coloraxis_showscale=False)
    st.plotly_chart(fig_prod, use_container_width=True)

with row2_col2:
    act_agg = (
        filtered_df.groupby(["IsActiveMember", "Gender"], observed=False)["Exited"]
        .agg(Total="count", Churned="sum", ChurnRate="mean")
        .reset_index()
    )
    act_agg["Activity"] = act_agg["IsActiveMember"].map({1: "Active Member", 0: "Inactive Member"})
    act_agg["ChurnRatePct"] = act_agg["ChurnRate"] * 100
    fig_act = px.bar(
        act_agg,
        x="Activity",
        y="ChurnRatePct",
        color="Gender",
        barmode="group",
        text=act_agg["ChurnRatePct"].apply(lambda v: f"{v:.1f}%"),
        title="Churn Rate by Activity & Gender",
        labels={"ChurnRatePct": "Churn Rate (%)"},
        color_discrete_map={"Female": "#EC4899", "Male": "#3B82F6"},
    )
    fig_act.update_layout(get_plotly_layout("Churn Rate by Activity & Gender"))
    st.plotly_chart(fig_act, use_container_width=True)
