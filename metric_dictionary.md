# PulseIQ Metric Dictionary

| Metric ID | Metric Name | Business Definition | Formula | Source Table |
|---|---|---|---|---|
| M01 | Headcount | Active employees on the last day of the month (permanent and contract). | Count distinct employee_id where hire_date <= month_end and (exit_date is null or exit_date > month_end) | fact_headcount_monthly |
| M02 | Hires | Employees whose hire_date falls in the month. | Count employee_id where hire_date is in the month | fact_headcount_monthly |
| M03 | Exits | Employees whose exit_date falls in the month. | Count employee_id where exit_date is in the month | fact_headcount_monthly |
| M04 | Attrition Rate (Monthly) | Share of people who left in the month. | Exits / Headcount at start × 100 | fact_headcount_monthly |
| M05 | Attrition Rate (Rolling 12 Months) | Leavers in the last 12 months divided by average headcount over the same period. | SUM(exits, 12 months) / AVG(headcount_end, 12 months) × 100 | fact_headcount_monthly |

## Notes

- These are the first five metrics from the official PulseIQ metric dictionary.
- Use the official business definitions and formulas.
- The source workbook defines these metrics using `fact_headcount_monthly`.
- The current ETL pipeline does not yet generate `fact_headcount_monthly`; this table is part of a later task.
