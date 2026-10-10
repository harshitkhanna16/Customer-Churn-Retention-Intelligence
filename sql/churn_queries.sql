-- Analytical SQL Queries for Customer Churn Intelligence

-- 1. Executive Summary: Total customers, churned customers, retained, churn rate, retention rate
-- NAME: executive_summary
SELECT 
    COUNT(*) AS TotalCustomers,
    SUM(Exited) AS ChurnedCustomers,
    SUM(CASE WHEN Exited = 0 THEN 1 ELSE 0 END) AS RetainedCustomers,
    ROUND(AVG(Exited), 4) AS ChurnRate,
    ROUND(1.0 - AVG(Exited), 4) AS RetentionRate,
    ROUND(SUM(Balance), 2) AS TotalBalance,
    ROUND(SUM(CASE WHEN Exited = 1 THEN Balance ELSE 0 END), 2) AS ChurnedBalance,
    ROUND(SUM(CASE WHEN Exited = 1 THEN Balance ELSE 0 END) / SUM(Balance), 4) AS ChurnedBalanceShare
FROM customers;

-- 2. Churn by Geography
-- NAME: churn_by_geography
SELECT 
    Geography,
    COUNT(*) AS TotalCustomers,
    SUM(Exited) AS ChurnedCustomers,
    ROUND(AVG(Exited), 4) AS ChurnRate,
    ROUND(SUM(Balance), 2) AS TotalDeposits,
    ROUND(AVG(Balance), 2) AS AvgBalance
FROM customers
GROUP BY Geography
ORDER BY ChurnRate DESC;

-- 3. Churn by Gender
-- NAME: churn_by_gender
SELECT 
    Gender,
    COUNT(*) AS TotalCustomers,
    SUM(Exited) AS ChurnedCustomers,
    ROUND(AVG(Exited), 4) AS ChurnRate
FROM customers
GROUP BY Gender
ORDER BY ChurnRate DESC;

-- 4. Churn by Age Group
-- NAME: churn_by_age_group
SELECT 
    AgeGroup,
    COUNT(*) AS TotalCustomers,
    SUM(Exited) AS ChurnedCustomers,
    ROUND(AVG(Exited), 4) AS ChurnRate
FROM customers
GROUP BY AgeGroup
ORDER BY 
    CASE AgeGroup 
        WHEN '<30' THEN 1 
        WHEN '30-40' THEN 2 
        WHEN '40-50' THEN 3 
        WHEN '50-60' THEN 4 
        WHEN '60+' THEN 5 
    END;

-- 5. Churn by Tenure Group
-- NAME: churn_by_tenure_group
SELECT 
    TenureGroup,
    COUNT(*) AS TotalCustomers,
    SUM(Exited) AS ChurnedCustomers,
    ROUND(AVG(Exited), 4) AS ChurnRate
FROM customers
GROUP BY TenureGroup
ORDER BY 
    CASE TenureGroup 
        WHEN '0-2y' THEN 1 
        WHEN '3-5y' THEN 2 
        WHEN '6-8y' THEN 3 
        WHEN '9-10y' THEN 4 
    END;

-- 6. Churn by Number of Products
-- NAME: churn_by_num_products
SELECT 
    NumOfProducts,
    COUNT(*) AS TotalCustomers,
    SUM(Exited) AS ChurnedCustomers,
    ROUND(AVG(Exited), 4) AS ChurnRate
FROM customers
GROUP BY NumOfProducts
ORDER BY NumOfProducts ASC;

-- 7. Churn by Activity Status
-- NAME: churn_by_activity
SELECT 
    CASE WHEN IsActiveMember = 1 THEN 'Active' ELSE 'Inactive' END AS ActivityStatus,
    COUNT(*) AS TotalCustomers,
    SUM(Exited) AS ChurnedCustomers,
    ROUND(AVG(Exited), 4) AS ChurnRate
FROM customers
GROUP BY IsActiveMember
ORDER BY ChurnRate DESC;

-- 8. Financial Exposure Analysis
-- NAME: financial_exposure
SELECT 
    ROUND(SUM(Balance), 2) AS TotalDeposits,
    ROUND(SUM(CASE WHEN Exited = 1 THEN Balance ELSE 0 END), 2) AS ChurnedDeposits,
    ROUND(SUM(CASE WHEN Exited = 0 THEN Balance ELSE 0 END), 2) AS RetainedDeposits,
    ROUND(AVG(CASE WHEN Exited = 1 THEN Balance ELSE NULL END), 2) AS AvgBalanceChurned,
    ROUND(AVG(CASE WHEN Exited = 0 THEN Balance ELSE NULL END), 2) AS AvgBalanceRetained
FROM customers;

-- 9. High-Risk Vulnerable Segment Prioritization
-- NAME: high_risk_segments
SELECT 
    Geography,
    AgeGroup,
    IsActiveMember,
    COUNT(*) AS SegmentSize,
    SUM(Exited) AS ChurnedCount,
    ROUND(AVG(Exited), 4) AS SegmentChurnRate,
    ROUND(SUM(Balance), 2) AS TotalBalanceExposed
FROM customers
GROUP BY Geography, AgeGroup, IsActiveMember
HAVING COUNT(*) >= 50
ORDER BY SegmentChurnRate DESC
LIMIT 10;
