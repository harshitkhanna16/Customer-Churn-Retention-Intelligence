"""Page 7: Retention Intelligence & Business ROI Simulation."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.utils.config import Config
from src.utils.ui import (
    apply_custom_styles,
    get_plotly_layout,
    render_kpi_card,
)

st.set_page_config(page_title="Retention Insights", page_icon="🎯", layout="wide")
apply_custom_styles()

st.title("🎯 Retention Insights & Playbook")
st.markdown(
    "<p class='page-subtitle'>Segment Playbooks, Hypotheses Tracker, and Financial Retention ROI Simulator</p>",
    unsafe_allow_html=True,
)

if not Config.POWERBI_EXPORT_PATH.exists():
    st.error("Portfolio dataset not found. Please train model first.")
    st.stop()

df = pd.read_csv(Config.POWERBI_EXPORT_PATH)
high_risk_df = df[df["RiskTier"] == "High Risk"]
high_risk_count = len(high_risk_df)
high_risk_deposits = float(high_risk_df["Balance"].sum())

# 1. Retention Strategy Playbook Table
st.subheader("1. Operational Retention Action Playbook")

playbook_data = [
    {
        "Target Segment": "Single Product Accounts (1 Product)",
        "Observed Churn Rate": "27.71%",
        "Baseline Comparison": "3.6x higher than 2-Product Accounts (7.58%)",
        "Prescribed Intervention": "Product Cross-Sell Incentive: Offer bundled high-yield savings or cash-back debit card with zero monthly maintenance fee for 12 months.",
        "Operational Department": "Retail Banking Marketing",
        "Data Evidence Level": "Empirical Observation",
    },
    {
        "Target Segment": "German Customer Accounts",
        "Observed Churn Rate": "32.44%",
        "Baseline Comparison": "2x higher than France (16.15%) and Spain (16.67%)",
        "Prescribed Intervention": "Regional Branch Concierge: Conduct localized relationship review, deposit yield benchmarking against local German fintechs, and dedicated hotline support.",
        "Operational Department": "German Regional Branch Network",
        "Data Evidence Level": "Empirical Observation",
    },
    {
        "Target Segment": "Multi-Product High-Tier (3+ Products)",
        "Observed Churn Rate": "85.89%",
        "Baseline Comparison": "Catastrophic attrition surge (3 prods: 82.7%, 4 prods: 100%)",
        "Prescribed Intervention": "Fee Rationalization & Portfolio Audit: High product count is associated with extreme churn, suggesting fee stacking or bundling friction. Perform proactive fee waiver review.",
        "Operational Department": "Private & Commercial Client Care",
        "Data Evidence Level": "Empirical Observation",
    },
    {
        "Target Segment": "Inactive Members (IsActiveMember = 0)",
        "Observed Churn Rate": "26.85%",
        "Baseline Comparison": "1.9x higher than Active Members (14.27%)",
        "Prescribed Intervention": "Digital Banking Re-Activation: Send targeted mobile push/email promotions highlighting automated recurring savings, direct deposit incentives, or free credit monitoring.",
        "Operational Department": "Digital Banking Product Team",
        "Data Evidence Level": "Empirical Observation",
    },
    {
        "Target Segment": "Mature Age Cohort (50-60 Years)",
        "Observed Churn Rate": "56.21%",
        "Baseline Comparison": "Highest attrition cohort in the entire institution",
        "Prescribed Intervention": "Senior Wealth Advisory: Provide complimentary estate and retirement asset review with a certified financial planner to anchor long-term deposits.",
        "Operational Department": "Wealth Management",
        "Data Evidence Level": "Empirical Observation",
    },
]

st.dataframe(pd.DataFrame(playbook_data), use_container_width=True, hide_index=True)

st.markdown("---")

# 2. Financial ROI Simulator
st.subheader("2. Retention Campaign Financial ROI Simulator")
st.markdown("Simulate the economic impact of proactive outreach targeting the **high-risk customer tier**:")

sim_col1, sim_col2 = st.columns([1, 2])

with sim_col1:
    st.markdown("##### Campaign Assumptions")
    success_rate = st.slider(
        "Intervention Retention Success Rate (%):",
        min_value=5,
        max_value=50,
        value=25,
        step=5,
        help="Percentage of contacted high-risk customers who are successfully saved from churn.",
    ) / 100.0

    net_margin = st.slider(
        "Net Interest Margin / Deposit Spread (%):",
        min_value=1.0,
        max_value=5.0,
        value=2.5,
        step=0.25,
        help="Annual net return the bank generates on preserved customer deposits.",
    ) / 100.0

    outreach_cost = st.number_input(
        "Cost per Customer Outreach ($):",
        min_value=5.0,
        max_value=250.0,
        value=25.0,
        step=5.0,
        help="Direct cost of relationship manager time, direct mail, or incentive offer.",
    )

    # Compute outcomes
    sim_saved_customers = int(high_risk_count * success_rate)
    sim_saved_deposits = float(high_risk_deposits * success_rate)
    sim_gross_income_saved = sim_saved_deposits * net_margin
    sim_campaign_cost = high_risk_count * outreach_cost
    sim_net_roi_dollar = sim_gross_income_saved - sim_campaign_cost
    sim_roi_pct = (sim_net_roi_dollar / sim_campaign_cost * 100) if sim_campaign_cost > 0 else 0.0

with sim_col2:
    st.markdown("##### Projected Financial Yield")
    k1, k2 = st.columns(2)
    with k1:
        render_kpi_card(
            "Customers Retained",
            f"{sim_saved_customers:,}",
            f"{success_rate*100:.0f}% of {high_risk_count:,} high-risk pool",
        )
        render_kpi_card(
            "Deposits Preserved",
            f"${sim_saved_deposits/1e6:.2f}M",
            f"Out of ${high_risk_deposits/1e6:.2f}M exposed deposits",
        )
    with k2:
        render_kpi_card(
            "Campaign Outreach Cost",
            f"${sim_campaign_cost:,.0f}",
            f"${outreach_cost:.0f} per account x {high_risk_count:,} accounts",
        )
        render_kpi_card(
            "Net Value Created (Annual)",
            f"${sim_net_roi_dollar/1e6:.2f}M",
            f"ROI: +{sim_roi_pct:.0f}% on campaign spend",
        )

st.markdown("---")
st.info(
    "⚖️ **Scientific Honesty & Causal Disclaimer:** "
    "All ROI projections above are business simulations based on user assumptions. "
    "Prior to executing full campaigns, run a randomized controlled trial (A/B test with a holdout control group) "
    "to measure actual campaign lift and verify causal retention impact."
)
