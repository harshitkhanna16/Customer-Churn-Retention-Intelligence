# SQL Analytical Queries Documentation

## 1. Overview
The analytical query layer operates directly on the embedded SQLite database (`data/customer_churn.db`), populated with both raw and feature-engineered records. All analytical queries are defined in `sql/churn_queries.sql` and exposed through `src.database.DatabaseManager`.

---

## 2. Query Catalogue & Business Application

### Query 1: `executive_summary`
- **Purpose:** Calculates overarching portfolio counts, historical churn rate, retention rate, total deposit balance, and churned deposit share.
- **Reconciliation:** Output reconciles 100% with Pandas calculations:
  - Total Customers = 10,000
  - Churned Customers = 2,037 (20.37%)
  - Total Deposits = $764,858,892.88
  - Churned Deposits = $185,588,094.63 (24.26% of deposits)

### Query 2: `churn_by_geography`
- **Purpose:** Summarizes customer counts, churn volumes, churn percentages, and total deposits grouped by retail banking market (`France`, `Germany`, `Spain`).
- **Core Insight:** Germany has 2,509 customers with 814 churners (**32.44% churn rate**), holding $300.4M in deposits, compared to France (16.15%) and Spain (16.67%).

### Query 3: `churn_by_gender`
- **Purpose:** Bivariate churn rate grouped by customer gender.
- **Core Insight:** Female customers churn at **25.07%** vs Male customers at **16.46%**.

### Query 4: `churn_by_age_group`
- **Purpose:** Tracks customer attrition across engineered age cohorts (`<30`, `30-40`, `40-50`, `50-60`, `60+`).
- **Core Insight:** Attrition accelerates sharply above age 40 (33.97%) and peaks in the 50-60 cohort at **56.21%**, while customers under 30 churn at only **7.52%**.

### Query 5: `churn_by_tenure_group`
- **Purpose:** Evaluates relationship duration effects across tenure buckets (`0-2y`, `3-5y`, `6-8y`, `9-10y`).
- **Core Insight:** Churn remains relatively consistent across tenure (18.87% to 21.15%), indicating that tenure alone does not insulate accounts from churn drivers.

### Query 6: `churn_by_num_products`
- **Purpose:** Evaluates customer retention based on number of active products held.
- **Core Insight:** Accounts with 2 products exhibit the lowest churn (**7.58%**). 1-product accounts churn at **27.71%**, while 3-product (82.71%) and 4-product (100%) accounts demonstrate acute attrition.

### Query 7: `churn_by_activity`
- **Purpose:** Compares active members (`IsActiveMember = 1`) against inactive members (`IsActiveMember = 0`).
- **Core Insight:** Inactive members churn at **26.85%** compared to active members at **14.27%** (a 1.88x multiple).

### Query 8: `financial_exposure`
- **Purpose:** Aggregates total bank deposits, deposits held by churned customers, and average balances of churned vs retained accounts.
- **Core Insight:** Churned customers hold a higher average deposit balance ($91,108.54) than retained customers ($72,745.30), reflecting elevated churn among German and mature clients who hold substantial balances.

### Query 9: `high_risk_segments`
- **Purpose:** Multi-dimensional ranking prioritizing segments by highest churn rate among cohorts with at least 50 clients.
- **Core Insight:** Highlights inactive German customers aged 50-60 as the most fragile cohort in the institution (**88.55% empirical churn rate**).

---

## 3. Execution & Verification Instructions

To execute and verify all queries from the command line:

```bash
# Using Python DatabaseManager
python -c "
from src.database.db_manager import DatabaseManager
db = DatabaseManager()
for name, sql in db.load_named_queries().items():
    df = db.execute_named_query(name)
    print(f'{name}: {len(df)} rows returned')
"

# Or using the SQLite CLI directly
sqlite3 data/customer_churn.db < sql/churn_queries.sql
```
