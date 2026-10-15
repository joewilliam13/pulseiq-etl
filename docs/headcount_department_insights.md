# Task 3 – Dashboard Design Review

## 1. Objective
To design and build an interactive HR Headcount and Departments dashboard using Apache Superset connected to the PulseIQ PostgreSQL data warehouse.

## 2. Dashboard Overview
Dashboard Name: PulseIQ – Headcount & Departments

The dashboard provides workforce insights through KPI cards, charts, filters, and a business insights section.

## 3. Charts Created
- Current Headcount
- Headcount Trend
- Headcount by Department
- Department Headcount Split
- Employee Tenure Bands
- Employee Role Mix
- Monthly Joiners vs Leavers

## 4. Filters
- Department filter
- Date Range filter

The Department filter was tested successfully. The Date Range filter was added, but its impact on every chart requires further validation.

## 5. Design Review and Improvements
- Used a consistent dashboard title and chart naming convention.
- Grouped the key headcount KPI and supporting charts into a single dashboard.
- Added a Key Business Insights section to communicate workforce analysis objectives.
- Added interactive filtering to support department-level analysis.
- Used a separate date-based database view to expose a proper date column for time filtering.
- Improved the layout by adjusting the space allocated to the insights section.

## 6. Data and Validation
The dashboard uses datasets connected to the PulseIQ PostgreSQL data warehouse.

Chart aggregation settings were reviewed, including the use of SUM for monthly headcount totals. Final reconciliation of all displayed chart values against warehouse SQL results is still required.

## 7. Export
Dashboard export files were extracted into the project’s `dashboards/` directory. The folder contains chart YAML files and dashboard, dataset, database, and metadata definitions.

Note: The Superset CLI export command reported an error during one attempt. The extracted export contents should be validated before treating the export as fully successful.

## 8. Conclusion
The PulseIQ Headcount & Departments dashboard was created in Apache Superset. It provides a foundation for exploring workforce size, department distribution, employee tenure, role mix, and monthly hiring and exits. Final data reconciliation and date-filter validation are the remaining quality checks.