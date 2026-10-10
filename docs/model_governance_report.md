# Machine Learning Model Governance & Benchmark Report

## 1. Governance & Training Protocol Overview

| Governance Dimension | Implementation Standard | Audit Status |
| :--- | :--- | :--- |
| **Dataset Source** | Historical retail banking dataset (`Churn_Modelling.csv`) | Verified (10,000 rows, 14 columns) |
| **Target Variable** | Binary `Exited` (1 = churned, 0 = retained) | Verified (20.37% churn, 79.63% retained) |
| **Data Partitioning** | 64% Training (6,400), 16% Validation (1,600), 20% Held-Out Test (2,000) | Stratified by target, Seed = 42 |
| **Data Leakage Controls** | Preprocessing (StandardScaler, OneHotEncoder) fit exclusively on `X_train` | Verified zero test-set exposure |
| **Cutoff Optimization** | F1-optimal probability threshold tuned strictly on validation split (`X_val`) | Zero optimization on test set |
| **Class Imbalance Strategy** | `scale_pos_weight = 3.91` (XGBoost), `class_weight='balanced'` (LogReg/RF) | Verified |

---

## 2. Benchmark Comparison on Held-Out Test Set (2,000 Records)

All metrics below are computed on the identical 2,000 held-out test records at their respective validation-tuned cutoffs:

| Candidate Model | Tuned Cutoff | ROC-AUC | PR-AUC | Accuracy | Precision (Class 1) | Recall (Class 1) | F1-Score | Recall vs Baseline |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dummy Baseline (Stratified)** | 0.10 | 0.4885 | 0.2699 | 66.60% | 18.55% | 18.92% | 0.1873 | Baseline Reference |
| **Logistic Regression** | 0.57 | 0.7965 | 0.5529 | 76.60% | 44.77% | 64.13% | 0.5273 | +45.2 pp (+238.9%) |
| **Random Forest Classifier** | 0.44 | 0.8580 | 0.6715 | 82.15% | 54.77% | 70.52% | 0.6165 | +51.6 pp (+272.7%) |
| **XGBoost (Champion)** | **0.64** | **0.8664** | **0.7134** | **85.00%** | **63.34%** | **62.41%** | **0.6287** | **+43.5 pp (+229.9%)** |

*Note at Default Threshold (0.50):*  
XGBoost at 0.50 cutoff achieves **80.30% Accuracy** and **74.69% Recall**, identifying ~3 out of every 4 churners in the portfolio.

---

## 3. Confusion Matrix Analysis (Champion XGBoost @ 0.64 Cutoff)

```
                 Actual Retained (0)    Actual Churned (1)
Predicted Retained (0)   TN = 1,446            FN = 153
Predicted Churned (1)    FP = 147              TP = 254
Total Tested             1,593 Retained        407 Churned
```

### Business Implications:
- **True Positives (254 accounts):** High-risk churners correctly caught and prioritized for retention campaigns.
- **False Positives (147 accounts):** Retained customers contacted with unnecessary retention outreach. Estimated outreach cost is ~$25 per customer (~$3,675 total exposure), which is negligible compared to losing customer relationships.
- **False Negatives (153 accounts):** Churners missed by the model at this conservative threshold. Adjusting the cutoff slider in the Streamlit application to `0.50` drops False Negatives down to **103 accounts**, recovering 50 additional at-risk relationships.

---

## 4. Top Feature Importances (XGBoost)

1. **`NumOfProducts` (0.1146):** Decisive feature; accounts holding 1 product or 3+ products show dramatic attrition anomalies.
2. **`AgeGroup_30-40` & `Age` (0.0941 & 0.0780):** Attrition rate accelerates past age 40, peaking at 56.2% between ages 50 and 60.
3. **`IsActive_x_NumOfProducts` (0.0689):** Interaction between engagement and portfolio breadth.
4. **`IsActiveMember` (0.0655):** Active digital usage is a potent protective factor against attrition.
5. **`Geography_Germany` (0.0515):** German accounts exhibit double the baseline attrition rate of France or Spain.
6. **`HasZeroBalance` (0.0591):** Non-zero balance accounts have higher churn vulnerability in this dataset.

---

## 5. Explainability & Causal Disclaimers
Local prediction explanations utilize **SHAP TreeExplainer**. SHAP values quantify how individual feature states shift model output relative to the portfolio baseline expectation (`0.049` log-odds). These attributions represent statistical associations within historical observational data and must not be interpreted as proving causal mechanisms.
