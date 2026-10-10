"""UI utilities and styling helpers for Streamlit application.

Provides unified styling, KPI cards, Plotly theme configurations,
and cached data/model accessors.
"""

from typing import Any, Dict, List, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data.loader import load_raw_data
from src.features.engineering import engineer_features_df
from src.models.registry import (
    load_best_model,
    load_evaluation_summary,
    load_model_metadata,
    load_preprocessor,
)
from src.utils.config import Config


def apply_custom_styles():
    """Inject custom CSS for styling across all pages."""
    custom_css = """
    <style>
        /* Modern Typography and Layout */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Metric Card Container */
        .metric-card {
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            transition: transform 0.15s ease-in-out, border-color 0.15s ease-in-out;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            border-color: #0284C7;
        }
        .metric-label {
            font-size: 0.82rem;
            color: #94A3B8;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
        }
        .metric-value {
            font-size: 1.85rem;
            font-weight: 700;
            color: #F8FAFC;
            margin-bottom: 4px;
        }
        .metric-subtext {
            font-size: 0.78rem;
            color: #64748B;
        }

        /* Risk Badges */
        .badge-low {
            background-color: rgba(16, 185, 129, 0.15);
            color: #10B981;
            padding: 4px 10px;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.8rem;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        .badge-med {
            background-color: rgba(245, 158, 11, 0.15);
            color: #F59E0B;
            padding: 4px 10px;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.8rem;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }
        .badge-high {
            background-color: rgba(239, 68, 68, 0.15);
            color: #EF4444;
            padding: 4px 10px;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.8rem;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        /* Header Subtitle */
        .page-subtitle {
            font-size: 1.05rem;
            color: #94A3B8;
            margin-top: -12px;
            margin-bottom: 24px;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_kpi_card(
    title: str, value: str, subtext: str = "", delta: Optional[str] = None
):
    """Render a styled KPI card in HTML."""
    delta_html = f"<div class='metric-subtext'>{subtext}</div>" if subtext else ""
    card_html = f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)


@st.cache_data
def get_cached_processed_data() -> pd.DataFrame:
    """Load and cache processed customer dataset."""
    if Config.PROCESSED_DATA_PATH.exists():
        return pd.read_csv(Config.PROCESSED_DATA_PATH)
    raw = load_raw_data()
    return engineer_features_df(raw)


@st.cache_resource
def get_cached_model_and_preprocessor():
    """Load and cache champion model and preprocessor."""
    model = load_best_model()
    preprocessor = load_preprocessor()
    metadata = load_model_metadata()
    return model, preprocessor, metadata


@st.cache_data
def get_cached_eval_summary():
    """Load and cache evaluation summary."""
    return load_evaluation_summary()


def get_plotly_layout(title: str = "") -> Dict[str, Any]:
    """Return unified styling parameters for Plotly figures."""
    return dict(
        title=dict(text=title, font=dict(family="Inter", size=16, color="#F8FAFC")),
        paper_bgcolor="rgba(15, 23, 42, 0.0)",
        plot_bgcolor="rgba(15, 23, 42, 0.0)",
        font=dict(family="Inter", color="#94A3B8"),
        margin=dict(l=40, r=40, t=50, b=40),
        xaxis=dict(gridcolor="#334155", zerolinecolor="#334155"),
        yaxis=dict(gridcolor="#334155", zerolinecolor="#334155"),
        legend=dict(font=dict(color="#CBD5E1")),
    )
