# Power BI Data Model Specification

## 1. Operating System Environment Notice
- **Current Operating System:** macOS (Darwin ARM64).
- **Power BI Compatibility:** Microsoft Power BI Desktop is only officially supported on Windows OS.
- **Delivery Strategy:** To ensure 100% portfolio compliance without fabricating a `.pbix` binary on a non-Windows platform, this repository provides:
  1. The complete, validated, model-scored export: `data/exports/powerbi_churn_dataset.csv`.
  2. Star-schema dimensional data model specification and data dictionary.
  3. Formatted DAX measures (`powerbi/DAX_Measures.md`).
  4. Visual layout, drill-through, and refresh documentation (`powerbi/Dashboard_Design_Guide.md`).

---

## 2. Recommended Star-Schema Architecture

While `powerbi_churn_dataset.csv` can be imported as a single flat table (`Fact_Churn_Intelligence`), enterprise Power BI deployments benefit from a clean Star Schema:

```
           +---------------------+
           |    Dim_Geography    |
           +---------------------+
           | Geography (PK)      |
           | CountryCode         |
           | RegionRiskTier      |
           +----------+----------+
                      | 1
                      | 
                      | *
+---------------------+---------------------+       +-------------------+
|               Fact_Churn_Intelligence     |       |    Dim_RiskTier   |
+-------------------------------------------+       +-------------------+
| CustomerId (PK)                           | *   1 | RiskTier (PK)     |
| CreditScore                               |<------+ PriorityWeight    |
| Geography (FK)                            |       | SLA_Days          |
| Gender                                    |       +-------------------+
| Age, AgeGroup                             |
| Tenure, TenureGroup                       |
| Balance, EstimatedSalary                  |
| NumOfProducts, HasCrCard, IsActiveMember  |
| Exited (Actual Historical Binary)         |
| PredictedProbability (Continuous 0-1)     |
| RiskTier (FK)                             |
| RecommendedAction                         |
| ModelVersion, ScoringTimestamp            |
+-------------------------------------------+
```

---

## 3. Field Types and Semantic Classifications

| Column Name | Power BI Data Type | Data Category | Description |
| :--- | :--- | :--- | :--- |
| `CustomerId` | Integer (Int64) | Identifier | Unique customer identifier (Do not aggregate) |
| `Geography` | Text | Country/Region | Geographic market (France, Germany, Spain) |
| `Gender` | Text | Uncategorized | Demographic gender |
| `Age` | Integer (Int64) | Uncategorized | Customer age |
| `AgeGroup` | Text | Uncategorized | Cohort bin (<30, 30-40, 40-50, 50-60, 60+) |
| `Tenure` | Integer (Int64) | Uncategorized | Years with bank |
| `TenureGroup` | Text | Uncategorized | Duration bin (0-2y, 3-5y, 6-8y, 9-10y) |
| `Balance` | Decimal (Fixed) | Currency ($) | Total customer deposit balance held |
| `EstimatedSalary` | Decimal (Fixed) | Currency ($) | Annual estimated customer salary |
| `NumOfProducts` | Integer (Int64) | Uncategorized | Number of active bank products held (1-4) |
| `HasCrCard` | Integer / Boolean | Uncategorized | 1 = Has card, 0 = No card |
| `IsActiveMember` | Integer / Boolean | Uncategorized | 1 = Active engagement, 0 = Inactive |
| `Exited` | Integer (Int64) | Uncategorized | 1 = Churned, 0 = Retained |
| `PredictedProbability` | Decimal (Float) | Percentage (%) | Model predicted probability of churn [0.0 - 1.0] |
| `RiskTier` | Text | Uncategorized | Segment tier: Low Risk, Medium Risk, High Risk |
| `RecommendedAction` | Text | Uncategorized | Rule-based prescriptive retention playbook |
| `ModelVersion` | Text | Uncategorized | Serialized model tag (e.g., v1.0-XGBoost) |
| `ScoringTimestamp` | Date/Time | Uncategorized | ISO 8601 scoring timestamp |

---

## 4. Connection and Refresh Instructions

1. Launch **Power BI Desktop** (on Windows or via Virtual Machine / Cloud Workspace).
2. Click **Get Data** -> **Text/CSV**.
3. Select `data/exports/powerbi_churn_dataset.csv`.
4. In Power Query Editor:
   - Ensure `CustomerId` is typed as Text or Integer (Do Not Summarize).
   - Format `Balance` and `EstimatedSalary` as Currency ($).
   - Format `PredictedProbability` as Percentage (2 decimal places).
5. Click **Close & Apply**.
6. In the **Modeling** tab, click **New Measure** and paste the DAX definitions from `powerbi/DAX_Measures.md`.
7. Configure scheduled refresh by placing the CSV in an accessible network path or OneDrive/SharePoint folder.
