-- SQLite Database Schema for Customer Churn & Retention Intelligence

DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
    RowNumber INTEGER PRIMARY KEY,
    CustomerId INTEGER UNIQUE NOT NULL,
    Surname TEXT NOT NULL,
    CreditScore INTEGER NOT NULL,
    Geography TEXT NOT NULL,
    Gender TEXT NOT NULL,
    Age INTEGER NOT NULL,
    Tenure INTEGER NOT NULL,
    Balance REAL NOT NULL,
    NumOfProducts INTEGER NOT NULL,
    HasCrCard INTEGER NOT NULL,
    IsActiveMember INTEGER NOT NULL,
    EstimatedSalary REAL NOT NULL,
    Exited INTEGER NOT NULL,
    AgeGroup TEXT NOT NULL,
    TenureGroup TEXT NOT NULL,
    BalanceSalaryRatio REAL,
    CreditScoreAgeRatio REAL,
    HasZeroBalance INTEGER NOT NULL,
    IsActive_x_NumOfProducts INTEGER NOT NULL,
    ProductsPerTenure REAL
);

CREATE INDEX IF NOT EXISTS idx_customers_geography ON customers(Geography);
CREATE INDEX IF NOT EXISTS idx_customers_agegroup ON customers(AgeGroup);
CREATE INDEX IF NOT EXISTS idx_customers_exited ON customers(Exited);
CREATE INDEX IF NOT EXISTS idx_customers_active ON customers(IsActiveMember);

DROP TABLE IF EXISTS customer_predictions;
CREATE TABLE customer_predictions (
    CustomerId INTEGER PRIMARY KEY,
    PredictedProbability REAL NOT NULL,
    RiskCategory TEXT NOT NULL,
    ModelVersion TEXT NOT NULL,
    ScoredAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CustomerId) REFERENCES customers(CustomerId)
);

CREATE INDEX IF NOT EXISTS idx_pred_risk ON customer_predictions(RiskCategory);
CREATE INDEX IF NOT EXISTS idx_pred_prob ON customer_predictions(PredictedProbability);
