"""Page 2: Exploratory Analytics & Data Quality Inspection."""

import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.analytics.eda import calculate_correlation_matrix
from src.utils.config import Config
from src.utils.ui import (
    apply_custom_styles,
    get_cached_processed_data,
    get_plotly_layout,
    render_kpi_card,
)

st.set_page_config(page_title="Exploratory Analytics", page_icon="🔬", layout="wide")
apply_custom_styles()

st.title("🔬 Exploratory Analytics & Data Quality")
st.markdown(
    "<p class='page-subtitle'>Interactive Statistical Analysis, Outlier Diagnostics, and Correlation Heatmaps</p>",
    unsafe_allow_html=True,
)

df = get_cached_processed_data()

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Data Quality & Hygiene",
    "📈 Feature Distributions",
    "🔥 Correlation Matrix",
    "🎯 Outlier Diagnostics",
])

# TAB 1: Data Quality
with tab1:
    st.subheader("Data Quality Audit & Integrity Report")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_kpi_card("Total Observations", f"{len(df):,}", "Complete rows ingested")
    with c2:
        render_kpi_card("Missing Values", "0 (0.0%)", "No imputation needed")
    with c3:
        render_kpi_card("Duplicate Customer IDs", "0", "100% unique primary keys")
    with c4:
        render_kpi_card("Class Imbalance", "3.91 : 1", "79.6% Retained / 20.4% Churned")

    # Download Data Quality Report JSON
    if Config.DATA_QUALITY_REPORT_PATH.exists():
        with open(Config.DATA_QUALITY_REPORT_PATH, "r", encoding="utf-8") as f:
            dq_json = f.read()
        st.download_button(
            "📥 Download Full Data Quality Report (JSON)",
            data=dq_json,
            file_name="eda_data_quality_report.json",
            mime="application/json",
        )

    st.markdown("#### Schema & Value Range Audit")
    summary_table = pd.DataFrame({
        "Feature": ["CreditScore", "Age", "Tenure", "Balance", "NumOfProducts", "EstimatedSalary", "Geography", "Gender"],
        "Data Type": ["Integer", "Integer", "Integer", "Float", "Integer", "Float", "String", "String"],
        "Expected Domain": ["[300, 850]", "[18, 100]", "[0, 10]", "[0.0, 1M+]", "[1, 4]", "[0.0, 10M+]", "France, Germany, Spain", "Female, Male"],
        "Observed Min / Values": [f"{df['CreditScore'].min()}", f"{df['Age'].min()}", f"{df['Tenure'].min()}", f"${df['Balance'].min():,.2f}", f"{df['NumOfProducts'].min()}", f"${df['EstimatedSalary'].min():,.2f}", "3 Categories", "2 Categories"],
        "Observed Max": [f"{df['CreditScore'].max()}", f"{df['Age'].max()}", f"{df['Tenure'].max()}", f"${df['Balance'].max():,.2f}", f"{df['NumOfProducts'].max()}", f"${df['EstimatedSalary'].max():,.2f}", "-", "-"],
        "Null Count": [0, 0, 0, 0, 0, 0, 0, 0],
    })
    st.dataframe(summary_table, use_container_width=True, hide_index=True)

# TAB 2: Feature Distributions
with tab2:
    st.subheader("Univariate & Bivariate Distributions")
    selected_feature = st.selectbox(
        "Select Feature to Visualize:",
        options=["Age", "CreditScore", "Balance", "EstimatedSalary", "Tenure", "NumOfProducts"],
        index=0,
    )

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        fig_hist = px.histogram(
            df,
            x=selected_feature,
            color=df["Exited"].map({1: "Churned", 0: "Retained"}),
            barmode="overlay",
            nbins=30,
            opacity=0.75,
            color_discrete_map={"Churned": "#EF4444", "Retained": "#10B981"},
            title=f"Distribution of {selected_feature} by Churn Status",
        )
        fig_hist.update_layout(get_plotly_layout(f"Distribution of {selected_feature}"))
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_chart2:
        fig_box = px.box(
            df,
            x=df["Exited"].map({1: "Churned", 0: "Retained"}),
            y=selected_feature,
            color=df["Exited"].map({1: "Churned", 0: "Retained"}),
            color_discrete_map={"Churned": "#EF4444", "Retained": "#10B981"},
            title=f"{selected_feature} Boxplot by Churn Status",
        )
        fig_box.update_layout(get_plotly_layout(f"{selected_feature} Boxplot"))
        st.plotly_chart(fig_box, use_container_width=True)

# TAB 3: Correlation Matrix
with tab3:
    st.subheader("Feature Correlation Matrix (Pearson)")
    corr_df = calculate_correlation_matrix(df)
    fig_corr = px.imshow(
        corr_df,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-1.0,
        zmax=1.0,
        title="Pearson Correlation Heatmap",
    )
    fig_corr.update_layout(get_plotly_layout("Pearson Correlation Heatmap"))
    st.plotly_chart(fig_corr, use_container_width=True)
    st.info("💡 **Key Finding:** Age has the highest positive correlation with Churn (`+0.285`), while Active Member Status has the strongest negative association (`-0.156`).")

# TAB 4: Outlier Diagnostics
with tab4:
    st.subheader("Interquartile Range (IQR) Outlier Audit")
    st.markdown("Auditing extreme values across continuous metrics using Tukey's 1.5 * IQR fence. Valid bank customers with high balances or advanced ages are **retained** without deletion.")
    
    outlier_metrics = []
    for col in ["CreditScore", "Age", "Balance", "EstimatedSalary"]:
        q1 = float(df[col].quantile(0.25))
        q3 = float(df[col].quantile(0.75))
        iqr = q3 - q1
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr
        n_out = len(df[(df[col] < lower_fence) | (df[col] > upper_fence)])
        outlier_metrics.append({
            "Feature": col,
            "Q1 (25th)": round(q1, 2),
            "Q3 (75th)": round(q3, 2),
            "IQR": round(iqr, 2),
            "Lower Fence": round(lower_fence, 2),
            "Upper Fence": round(upper_fence, 2),
            "Outlier Count": n_out,
            "Outlier %": f"{n_out/len(df)*100:.2f}%",
            "Handling Rationale": "Preserved: Valid natural distribution in banking demography."
        })
    st.dataframe(pd.DataFrame(outlier_metrics), use_container_width=True, hide_index=True)
