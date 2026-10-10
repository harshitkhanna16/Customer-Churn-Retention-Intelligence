"""Page 4: Individual Customer Prediction & SHAP Explainability."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.predictions.scorer import score_single_customer
from src.utils.config import Config
from src.utils.ui import (
    apply_custom_styles,
    get_plotly_layout,
    render_kpi_card,
)

st.set_page_config(page_title="Individual Prediction", page_icon="👤", layout="wide")
apply_custom_styles()

st.title("👤 Individual Customer Prediction & Explainability")
st.markdown(
    "<p class='page-subtitle'>Interactive Customer Risk Scoring, SHAP Attribution, and Prescriptive Retention Playbook</p>",
    unsafe_allow_html=True,
)

with st.form("single_prediction_form"):
    st.subheader("Customer Profile Inputs")
    c1, c2, c3 = st.columns(3)

    with c1:
        credit_score = st.slider("Credit Score", min_value=350, max_value=850, value=650, step=5)
        geography = st.selectbox("Geography", options=["France", "Germany", "Spain"], index=1)
        gender = st.selectbox("Gender", options=["Female", "Male"], index=0)
        age = st.slider("Customer Age", min_value=18, max_value=90, value=48, step=1)

    with c2:
        tenure = st.slider("Tenure (Years)", min_value=0, max_value=10, value=3, step=1)
        balance = st.number_input("Account Balance ($)", min_value=0.0, max_value=1_000_000.0, value=115_000.0, step=1000.0)
        estimated_salary = st.number_input("Estimated Salary ($)", min_value=0.0, max_value=1_000_000.0, value=95_000.0, step=1000.0)

    with c3:
        num_products = st.selectbox("Number of Products", options=[1, 2, 3, 4], index=0)
        has_credit_card = st.selectbox("Holds Credit Card?", options=["Yes", "No"], index=0)
        is_active_member = st.selectbox("Active Engagement?", options=["Yes", "No"], index=1)

    submit_button = st.form_submit_button("⚡ Score Customer Risk", use_container_width=True)

# Prepare customer dict
customer_dict = {
    "CreditScore": credit_score,
    "Geography": geography,
    "Gender": gender,
    "Age": age,
    "Tenure": tenure,
    "Balance": balance,
    "NumOfProducts": num_products,
    "HasCrCard": 1 if has_credit_card == "Yes" else 0,
    "IsActiveMember": 1 if is_active_member == "Yes" else 0,
    "EstimatedSalary": estimated_salary,
}

# Run prediction
res = score_single_customer(customer_dict)
prob = res["churn_probability"]
prob_pct = res["churn_percentage"]
risk_tier = res["risk_tier"]
rec = res["recommendation"]
shap_data = res["explanation"]

st.markdown("---")
st.subheader("Prediction Intelligence & Risk Diagnostics")

score_col1, score_col2 = st.columns([1, 2])

with score_col1:
    # Gauge Chart
    badge_color = "#10B981" if risk_tier == "Low Risk" else ("#F59E0B" if risk_tier == "Medium Risk" else "#EF4444")
    
    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=prob_pct,
            number={"suffix": "%", "font": {"size": 36, "color": "#F8FAFC"}},
            title={"text": f"Predicted Risk: {risk_tier}", "font": {"size": 18, "color": badge_color}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#94A3B8"},
                "bar": {"color": badge_color},
                "bgcolor": "#1E293B",
                "borderwidth": 1,
                "bordercolor": "#334155",
                "steps": [
                    {"range": [0, 35], "color": "rgba(16, 185, 129, 0.2)"},
                    {"range": [35, 65], "color": "rgba(245, 158, 11, 0.2)"},
                    {"range": [65, 100], "color": "rgba(239, 68, 68, 0.2)"},
                ],
            },
        )
    )
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#F8FAFC", family="Inter"),
        height=280,
        margin=dict(l=20, r=20, t=30, b=20),
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    render_kpi_card("Action Priority", rec["priority_level"], rec["primary_action"])

with score_col2:
    st.markdown("#### 🔍 SHAP Local Explainability Attribution")
    st.caption("How specific customer attributes directional influence this prediction compared to portfolio baseline.")

    drivers = shap_data.get("top_risk_drivers", [])
    anchors = shap_data.get("top_retention_anchors", [])

    all_shap = [
        {"Feature": d["feature"], "Impact": d["impact"], "Direction": "Increases Risk"}
        for d in drivers
    ] + [
        {"Feature": a["feature"], "Impact": a["impact"], "Direction": "Decreases Risk"}
        for a in anchors
    ]

    if all_shap:
        shap_df = pd.DataFrame(all_shap)
        fig_shap = px.bar(
            shap_df,
            x="Impact",
            y="Feature",
            color="Direction",
            orientation="h",
            color_discrete_map={"Increases Risk": "#EF4444", "Decreases Risk": "#10B981"},
            title="Key Influencing Factors (SHAP Values)",
        )
        fig_shap.update_layout(get_plotly_layout("Key Influencing Factors"), yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig_shap, use_container_width=True)

st.markdown("---")

# Prescriptive Retention Section
st.subheader("🎯 Prescriptive Retention Recommendations")
for i, act in enumerate(rec["all_actions"], 1):
    st.markdown(f"**Step {i}:** {act}")

st.info(f"⚖️ **Governance Disclaimer:** {rec['disclaimer']}")
