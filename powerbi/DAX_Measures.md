# Power BI DAX Measures Specification

This document provides production-ready DAX measures designed to power the 4-page Customer Churn & Retention Intelligence dashboard.

---

## 1. Core Portfolio Volume & Churn Measures

### Total Customers
```dax
Total Customers = 
COUNTROWS('Fact_Churn_Intelligence')
```

### Churned Customers (Historical)
```dax
Churned Customers = 
CALCULATE(
    COUNTROWS('Fact_Churn_Intelligence'),
    'Fact_Churn_Intelligence'[Exited] = 1
)
```

### Retained Customers (Historical)
```dax
Retained Customers = 
CALCULATE(
    COUNTROWS('Fact_Churn_Intelligence'),
    'Fact_Churn_Intelligence'[Exited] = 0
)
```

### Overall Churn Rate %
```dax
Churn Rate % = 
DIVIDE([Churned Customers], [Total Customers], 0)
```

### Overall Retention Rate %
```dax
Retention Rate % = 
1 - [Churn Rate %]
```

---

## 2. Machine Learning Risk & Exposure Measures

### Predicted High Risk Customers
```dax
High Risk Customers = 
CALCULATE(
    COUNTROWS('Fact_Churn_Intelligence'),
    'Fact_Churn_Intelligence'[RiskTier] = "High Risk"
)
```

### High Risk Customer Share %
```dax
High Risk Share % = 
DIVIDE([High Risk Customers], [Total Customers], 0)
```

### Average Predicted Churn Probability
```dax
Avg Predicted Churn Probability = 
AVERAGE('Fact_Churn_Intelligence'[PredictedProbability])
```

### Total Customer Deposits Held (Balance)
```dax
Total Deposits = 
SUM('Fact_Churn_Intelligence'[Balance])
```

### Churned Account Deposits
```dax
Churned Deposits = 
CALCULATE(
    SUM('Fact_Churn_Intelligence'[Balance]),
    'Fact_Churn_Intelligence'[Exited] = 1
)
```

### High Risk Deposit Exposure
```dax
High Risk Deposits Exposed = 
CALCULATE(
    SUM('Fact_Churn_Intelligence'[Balance]),
    'Fact_Churn_Intelligence'[RiskTier] = "High Risk"
)
```

### High Risk Deposit Exposure Share %
```dax
High Risk Deposit Share % = 
DIVIDE([High Risk Deposits Exposed], [Total Deposits], 0)
```

---

## 3. Financial & Retention ROI Simulation Measures

### Retainable High Risk Customers (Assuming 25% Intervention Success)
```dax
Simulated Retained High Risk = 
[High Risk Customers] * 0.25
```

### Preserved Deposit Value ($)
```dax
Simulated Preserved Deposits = 
[High Risk Deposits Exposed] * 0.25
```

### Estimated Annual Interest Spread Preserved (at 2.5% Net Margin)
```dax
Estimated Annual Value Preserved = 
[Simulated Preserved Deposits] * 0.025
```
