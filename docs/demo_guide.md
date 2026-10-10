# Interactive Demonstration & Interview Walkthrough Guide

Use this step-by-step walkthrough to present a 5-to-10 minute live demonstration of the platform to engineering hiring managers, data science directors, or executive stakeholders.

---

## Act 1: The Executive Problem & Portfolio Baseline (2 Minutes)
1. **Launch the Web App:**
   ```bash
   streamlit run app.py
   ```
2. **Review System Health:** Point out the green system status cards confirming that 10,000 real customer records, the trained XGBoost champion model (ROC-AUC 0.866), and the embedded SQLite analytical database are live.
3. **Navigate to `1_Executive_Overview`:**
   - Highlight the 20.37% baseline churn rate and $764.86M in total customer deposits.
   - Clarify the financial governance distinction: *balance represents customer deposits held, not institutional fee income*.
   - Filter by Geography: Show how selecting Germany highlights a **32.44% churn rate** (double France and Spain).
   - Point out the age cohort curve: Attrition surges from 7.5% under age 30 to **56.2% between ages 50 and 60**.

---

## Act 2: Honest Model Governance & Threshold Optimization (3 Minutes)
1. **Navigate to `3_Model_Performance`:**
   - Walk through the benchmark comparison table comparing Dummy Baseline, Logistic Regression, Random Forest, and XGBoost on the identical 2,000 held-out test split.
   - Show how the dummy baseline captures only 18.9% recall, while XGBoost achieves **62.4% recall at 85.0% accuracy** (and **74.7% recall** at default 0.50 cutoff).
   - Display the ROC (0.866) and Precision-Recall (0.713) curves.
2. **Demonstrate the Decision Threshold Simulator:**
   - Move the probability threshold slider from 0.64 down to 0.40.
   - Show how the confusion matrix live updates: True Positives increase (capturing more churners) while False Positives rise.
   - Explain the business trade-off: In retail banking, the cost of an outreach email or phone call (~$25) is negligible compared to losing an average customer deposit balance ($76,000+).

---

## Act 3: Individual Customer Scoring & SHAP Attribution (2 Minutes)
1. **Navigate to `4_Individual_Prediction`:**
   - Configure a vulnerable customer: Age = 52, Geography = Germany, Balance = $125,000, NumOfProducts = 1, IsActiveMember = No.
   - Click **Score Customer Risk**.
   - Show the dynamic risk gauge needle jump into the **High Risk** zone (~85%+ probability).
   - Explain the SHAP feature attribution waterfall: Point out how `NumOfProducts = 1`, `Geography_Germany`, and `Age` directional push risk higher, while credit score acts as a partial anchor.
   - Review the tailored step-by-step retention recommendations.

---

## Act 4: Operational Batch Inference & Financial ROI (3 Minutes)
1. **Navigate to `5_Batch_Scoring`:**
   - Click **Download Sample CSV Template** or **Load Demo 50-Customer Batch**.
   - Demonstrate the schema validation step (confirming column presence and domain bounds).
   - Show the batch scored table, filter for High Risk accounts, and click **Download Scored Batch Predictions**.
2. **Navigate to `7_Retention_Insights`:**
   - Review the concrete segment playbook.
   - Adjust the **Campaign ROI Simulator** sliders (e.g. 25% retention success rate, 2.5% net margin).
   - Show how proactively intervening on the high-risk pool yields **multi-million dollar net deposit preservation** with high campaign ROI.
3. **Navigate to `8_Project_Information`:**
   - Review the architecture diagram and data dictionary.
   - Conclude with the model governance and interview defensibility card.
