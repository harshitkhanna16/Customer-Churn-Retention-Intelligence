# Technical Interview Questions & Defensible Answers

This guide prepares you for deep technical interview questions regarding the architecture, modeling decisions, business trade-offs, and governance protocols implemented in this project.

---

### Q1: "Why did you prioritize ROC-AUC and Recall over raw Accuracy on this dataset?"
**Answer:**  
"Because the dataset exhibits a classic retail banking class imbalance: 79.6% retained and 20.4% churned (roughly a 4:1 ratio). A naive baseline classifier that trivially predicts every customer will stay achieves ~80% accuracy, but has 0% recall and completely fails the business objective of catching churners.

We benchmarked a Dummy Baseline, Logistic Regression, Random Forest, and XGBoost on a held-out 2,000-customer test set. XGBoost delivered the highest **ROC-AUC (0.8664)** and **PR-AUC (0.7134)**. By optimizing the decision threshold on validation data, we achieved **85.00% accuracy** with **62.41% recall and 63.34% precision** (or **74.69% recall** at the default 0.50 cutoff, capturing 3 out of every 4 churners). This balances catching churners while controlling campaign outreach costs."

---

### Q2: "How did you prevent data leakage during feature engineering and model training?"
**Answer:**  
"Data leakage was systematically prevented through three architectural controls:
1. **Pipeline Encapsulation:** All numerical transformations (StandardScaler) and categorical encodings (OneHotEncoder) were packaged inside a Scikit-learn `Pipeline` alongside a custom `CustomerFeatureEngineer` transformer.
2. **Strict Fit Boundary:** `pipeline.fit()` was executed strictly on the training partition (`X_train`), never on the validation or test splits. The test partition was only transformed using the fitted state.
3. **Dedicated Threshold Tuning:** Probability decision cutoffs were optimized using out-of-sample predictions on a dedicated 16% validation split (`X_val`). The final 20% test partition (`X_test`) was left completely untouched until the final, unbiased evaluation."

---

### Q3: "What were the most important churn drivers uncovered, and how do they inform business strategy?"
**Answer:**  
"Both global feature importance and local SHAP explanations revealed four primary attrition drivers:
1. **Product Count:** Customers with 1 product churn at 27.7%, whereas those with 2 products churn at only 7.6% (a 3.6x drop). However, holding 3 or 4 products results in catastrophic churn (82.7% and 100%), likely reflecting account fee stacking or bundling dissatisfaction. Strategy: Proactively cross-sell a 2nd product, but audit fee structures on 3+ product accounts.
2. **Customer Age:** Churn accelerates after age 40 and peaks at 56.2% between ages 50 and 60. Strategy: Senior wealth preservation consultations and estate planning to retain mature balances.
3. **Geographic Disparity:** German accounts experience double the churn rate of France and Spain (32.4% vs 16.2%), despite holding the highest average balances. Strategy: Regional branch relationship outreach and deposit yield benchmarking.
4. **Member Activity:** Inactive members churn at 26.9% compared to 14.3% for active members. Strategy: Digital banking activation incentives."

---

### Q4: "How does the platform handle model explainability, and why is the distinction between attribution and causality important?"
**Answer:**  
"We integrated SHAP TreeExplainer for local model explainability. For any customer prediction, SHAP decomposes the predicted log-odds into additive contributions from each feature relative to the expected portfolio base value.

However, in financial data science, confusing statistical attribution with causal proof is dangerous. For instance, while high balance in German customers is strongly associated with churn in this dataset, forcing customers to lower their balances would not prevent churn! We explicitly document this in our governance cards and in the UI, advising stakeholders to use the model for targeted identification, but conduct randomized controlled trials (A/B testing with holdout groups) before scaling expensive retention interventions."

---

### Q5: "How did you design the system for production deployment and maintenance?"
**Answer:**  
"The codebase follows clean software engineering principles:
- **Modular Architecture:** Clear separation between data validation, feature engineering, modeling, inference, database analytics, and Streamlit presentation layers.
- **Artifact Serialization:** Models, pipelines, and evaluation metadata are versioned and persisted using `joblib` and JSON.
- **Batch Validation:** The batch inference endpoint strictly asserts schemas and domain ranges, catching corrupt records with clear row-level error reporting rather than silently dropping rows.
- **Relational Analytics:** An embedded SQLite database with 9 parameterized analytical SQL queries enables instant reporting and reconciles 100% with Python calculations.
- **Comprehensive Testing:** 16 automated Pytest tests validate data loading, feature engineering, probability bounds, model loading, and SQL consistency."
