# Power BI Dashboard Design Guide

A blueprint for constructing the 4-page Customer Churn & Retention Intelligence dashboard in Power BI.

---

## Page 1: Executive Overview
- **Objective:** Give C-level leaders instant visibility into total customer health, historical churn baseline, and high-risk deposit exposure.
- **Header:** Title, Refresh Date KPI, Geography Slicer (France, Germany, Spain), Gender Slicer.
- **Top Row KPI Cards:**
  1. `Total Customers` (Formatted with comma separator: 10,000)
  2. `Historical Churn Rate %` (20.37% - Red callout)
  3. `High Risk Customers` (Count & % of Portfolio)
  4. `Total Deposits Held` ($764.86M)
  5. `High Risk Deposit Exposure` ($ Amount & % share of deposits)
- **Visual 1 (Donut Chart):** Customer Risk Tier Breakdown (Low Risk: Green, Medium Risk: Amber, High Risk: Red).
- **Visual 2 (Clustered Bar Chart):** Historical Churn Rate by Geography vs Predicted High Risk Customers.
- **Visual 3 (Line Chart):** Churn Rate by Age Cohort (<30 to 60+).

---

## Page 2: Churn Drivers & Behavioral Analytics
- **Objective:** Deep-dive into behavioral signals causing attrition.
- **Visual 1 (100% Stacked Bar):** Churn Rate by `NumOfProducts` (Highlights massive surge at 3 and 4 products).
- **Visual 2 (Clustered Column):** Member Engagement (`IsActiveMember`) Churn Rate split across Countries.
- **Visual 3 (Scatter Plot):** `Age` (X-axis) vs `Balance` (Y-axis), colored by `RiskTier` with tooltips showing `CustomerId` and `PredictedProbability`.
- **Visual 4 (Matrix Table):** Cohort Heatmap: `AgeGroup` (Rows) by `Geography` (Columns) displaying Average Churn Rate and Total Customer Balance.

---

## Page 3: Customer Risk Intelligence & Machine Learning
- **Objective:** Operational risk exploration for frontline credit and retention managers.
- **Slicers:** Risk Tier filter, Geography filter, Products filter, Predicted Probability Range Slider [0.0 - 1.0].
- **Visual 1 (Histogram / Density):** Distribution of Predicted Churn Probabilities across the portfolio.
- **Visual 2 (Table Visual):** High Risk Customer Queue:
  - Columns: `CustomerId`, `Geography`, `Age`, `Balance`, `NumOfProducts`, `PredictedProbability`, `RiskTier`, `RecommendedAction`.
  - Conditional formatting: Red background fill on `PredictedProbability > 0.65`.
  - Sort order: Descending by `PredictedProbability`.

---

## Page 4: Retention Playbook & Action Simulator
- **Objective:** Financial ROI simulation and operational action prioritization.
- **What-If Parameter (Slider):** `Intervention Success Rate %` (0% to 50%, Default: 25%).
- **Card Metrics:**
  - `Simulated Retained High Risk Customers`
  - `Simulated Preserved Deposits ($)`
  - `Estimated Annual Value Preserved ($)`
- **Visual 1 (Bar Chart):** Customer Count by `RecommendedAction` category (showing queue size per operational department).
- **Drill-Through Target:** Right-click any segment in Page 1 or 2 to drill through directly into customer contact queue on Page 4.
