
-- Query 1: Department-wise headcount
SELECT
    d.department_name,
    h.headcount_end
FROM dw.fact_headcount_monthly h
JOIN dw.dim_department d
    ON h.department_id = d.department_id
ORDER BY h.headcount_end DESC
LIMIT 10;


-- Query 2: Monthly gross payroll
SELECT
    d.year,
    d.month,
    ROUND(SUM(p.gross_pay), 2) AS total_gross_payroll
FROM dw.fact_payroll p
JOIN dw.dim_date d
    ON p.date_key = d.date_key
GROUP BY d.year, d.month
ORDER BY d.year, d.month;


-- Query 3: Leave status analysis
SELECT
    status,
    COUNT(*) AS total_requests,
    ROUND(SUM(days), 2) AS total_leave_days
FROM dw.fact_leave
GROUP BY status
ORDER BY total_requests DESC;
