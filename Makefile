# ==============================================================================
# Customer Churn & Retention Intelligence — Production Makefile
# ==============================================================================

SHELL := /bin/bash
PYTHON := .venv/bin/python
PYTEST := .venv/bin/pytest
STREAMLIT := .venv/bin/streamlit

.DEFAULT_GOAL := help

.PHONY: help all setup data db train test export run app clean

help: ## Show this help message and target descriptions
	@echo ""
	@echo "🏦 Customer Churn & Retention Intelligence — Build Automation"
	@echo "=============================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'
	@echo ""

all: data db train export test ## Run complete end-to-end pipeline (Data -> DB -> Train -> Export -> Test)
	@echo "✅ Complete pipeline successfully executed and verified!"

setup: ## Install dependencies into .venv
	@echo "📦 Installing project dependencies..."
	$(PYTHON) -m pip install -r requirements.txt

data: ## Validate raw dataset and produce processed feature dataset
	@echo "🔍 Validating raw dataset and generating processed features..."
	$(PYTHON) -c "from src.data.loader import load_raw_data, save_processed_data; from src.data.validator import DataValidator; from src.features.engineering import engineer_features_df; df = load_raw_data(); v = DataValidator(df); v.save_report(); df_proc = engineer_features_df(df); save_processed_data(df_proc); print('Data processed and validated successfully!')"
	$(PYTHON) scripts/create_eda_notebook.py

db: ## Initialize SQLite database and populate customer tables
	@echo "🗄️ Initializing SQLite database and loading customer records..."
	$(PYTHON) -c "from src.database.db_manager import init_database; db = init_database(); print('SQLite database initialized at data/customer_churn.db')"

train: ## Train all candidate models, optimize validation thresholds, and save artifacts
	@echo "⚡ Training Logistic Regression, Random Forest, and XGBoost models..."
	$(PYTHON) -m src.models.train

export: ## Generate Power BI export dataset and sample batch CSV
	@echo "📊 Generating Power BI scored dataset and sample batch CSV..."
	$(PYTHON) -c "from src.data.loader import load_raw_data; from src.features.engineering import engineer_features_df; from src.predictions.scorer import score_batch_customers; from datetime import datetime; df_raw = load_raw_data(); df_proc = engineer_features_df(df_raw); feats = [c for c in df_raw.columns if c not in ['RowNumber', 'CustomerId', 'Surname', 'Exited']]; scored = score_batch_customers(df_raw[feats]); df_proc['PredictedProbability'] = scored['PredictedProbability']; df_proc['RiskTier'] = scored['RiskTier']; df_proc['RecommendedAction'] = scored['RecommendedAction']; df_proc['ModelVersion'] = 'v1.0-XGBoost'; df_proc['ScoringTimestamp'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%SZ'); df_proc.to_csv('data/exports/powerbi_churn_dataset.csv', index=False); print('Power BI export generated successfully!')"

test: ## Run automated Pytest test suite
	@echo "🧪 Running automated test suite..."
	$(PYTHON) -m pytest tests/ -v

run: ## Launch Streamlit web application
	@echo "🚀 Launching Streamlit web application..."
	$(STREAMLIT) run app.py

app: run ## Alias for run

clean: ## Remove caches, bytecode, and temporary files
	@echo "🧹 Cleaning temporary files and caches..."
	rm -rf __pycache__ src/**/__pycache__ tests/__pycache__ .pytest_cache .uv_cache
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "Clean completed."
