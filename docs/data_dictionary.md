# Comprehensive Data Dictionary

## 1. Raw Dataset Attributes (`Churn_Modelling.csv`)

| Field Name | Storage Type | Domain Range | Nullable | Role in System | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `RowNumber` | Integer | [1, 10000] | No | Identifier | Sequential file row index. Excluded from predictive modeling. |
| `CustomerId` | Integer | [15565701, 15815690] | No | Identifier / Primary Key | Unique 8-digit client identifier. Retained for joins, excluded from feature inputs. |
| `Surname` | String | Alphabetical text | No | Descriptive / Masked | Customer family name. Excluded from modeling to avoid demographic/surname bias. |
| `CreditScore` | Integer | [350, 850] | No | Predictive Feature | Numerical credit rating evaluated by credit bureau. |
| `Geography` | String | France, Germany, Spain | No | Predictive Feature | Primary country of retail banking relationship. |
| `Gender` | String | Female, Male | No | Predictive Feature | Binary biological gender. |
| `Age` | Integer | [18, 92] | No | Predictive Feature | Customer biological age. Strongest single predictor of churn. |
| `Tenure` | Integer | [0, 10] | No | Predictive Feature | Number of completed years customer has maintained bank relationship. |
| `Balance` | Float | [$0.00, $250,898.09] | No | Predictive Feature / Exposure | Total deposits held in customer accounts. 3,617 customers hold exactly $0.00. |
| `NumOfProducts` | Integer | [1, 2, 3, 4] | No | Predictive Feature | Total number of financial products subscribed (e.g., checking, savings, credit, loan). |
| `HasCrCard` | Integer | {0, 1} | No | Predictive Feature | Binary indicator: 1 = customer possesses bank credit card, 0 = no credit card. |
| `IsActiveMember`| Integer | {0, 1} | No | Predictive Feature | Binary engagement status: 1 = regular digital/branch activity, 0 = dormant account. |
| `EstimatedSalary`| Float | [$11.58, $199,992.48] | No | Predictive Feature | Estimated annual customer income. |
| `Exited` | Integer | {0, 1} | No | **Target Variable** | Historical binary ground truth: 1 = account closed (churned), 0 = active client. |

---

## 2. Engineered Domain Features

| Field Name | Storage Type | Calculation Logic | Business Justification |
| :--- | :--- | :--- | :--- |
| `AgeGroup` | String / Categorical | Binned: `<30`, `30-40`, `40-50`, `50-60`, `60+` | Captures non-linear lifecycle stages (younger clients exhibit low churn; 50-60 cohort spikes to 56.2%). |
| `TenureGroup` | String / Categorical | Binned: `0-2y` (New), `3-5y` (Established), `6-8y` (Mature), `9-10y` (Veteran) | Disaggregates early relationship onboarding friction from long-term relationship fatigue. |
| `BalanceSalaryRatio` | Float | `Balance / (EstimatedSalary + 1.0)` | Differentiates deposit-heavy wealth preservers from paycheck-to-paycheck transactional users. |
| `CreditScoreAgeRatio`| Float | `CreditScore / Age` | Normalizes credit standing by customer age to isolate mature credit health. |
| `HasZeroBalance` | Binary | `1 if Balance == 0.0 else 0` | Isolates 36.2% of customer base with zero deposit balances (predominantly in France & Spain). |
| `IsActive_x_NumOfProducts` | Integer | `IsActiveMember * NumOfProducts` | Interaction term capturing product depth among engaged versus dormant accounts. |
| `ProductsPerTenure` | Float | `NumOfProducts / (Tenure + 1.0)` | Product adoption velocity per year of tenure. |

---

## 3. Model Inference Outputs & Power BI Export Fields

| Field Name | Storage Type | Calculation Logic | Description |
| :--- | :--- | :--- | :--- |
| `PredictedProbability` | Float [0.0 - 1.0] | `model.predict_proba(X)[:, 1]` | Model's estimated likelihood that the customer will churn in the forecast horizon. |
| `RiskTier` | String | `Low Risk (<0.35)`, `Medium Risk (0.35-0.65)`, `High Risk (>=0.65)` | Actionable operational priority tier for retention routing. |
| `RecommendedAction` | String | Rule-based heuristic tree | Prescribed retention intervention based on individual risk drivers. |
| `ModelVersion` | String | Static Tag (`v1.0-XGBoost`) | Audit version string tracking model provenance. |
| `ScoringTimestamp` | ISO 8601 String | UTC Timestamp | Exact date and time when record was scored. |
