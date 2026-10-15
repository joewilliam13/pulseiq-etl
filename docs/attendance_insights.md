# PulseIQ ETL – Task 4: Attendance & Leave Insights

## 1. Objective
Analyze monthly attendance, department-level attendance, leave usage, late arrivals, and sample AI-generated anomaly flags using the PulseIQ warehouse.

## 2. Key Findings

**Finding 1 – Monthly Attendance**
- September 2026 attendance rate was 95.00%.
- May 2026 recorded the lowest monthly attendance rate in the available period at 92.64%.
- Action: HR can review attendance patterns and investigate reasons for monthly changes.

**Finding 2 – Department Attendance**
- D08 recorded the lowest department-level attendance rate at 90.60%.
- Action: Review department-level workload, leave patterns, and attendance practices before deciding on corrective action.

**Finding 3 – Leave Usage**
- Earned Leave recorded 2,336 approved leave days.
- Casual Leave recorded 1,995 approved leave days.
- Action: Use leave trends to support workforce planning and coverage.

**Finding 4 – Late Arrivals**
- September 2026 recorded 618 late arrivals in the monthly attendance data.
- Action: Review late-arrival patterns and discuss possible causes with relevant teams.

**Finding 5 – AI Anomaly Flags**
- The sample results contain 221 attendance-related flagged records and 184 payroll-related flagged records.
- Action: Investigate flagged records and validate them against source data before taking action.

## 3. Data Quality and Limitations
- Daily weekday analysis uses 2,000 sample records, not the complete company attendance history.
- The monthly warehouse attendance table cannot independently establish daily weekday patterns.
- All 405 records in the supplied anomaly-results sample are flagged; a flag is not proof of a confirmed anomaly.
- Findings describe the available dataset and should not automatically be generalized to every employee or period.

## 4. Conclusion
The dashboard provides a consolidated view of attendance, leave, late arrivals, and sample anomaly flags. HR teams can use these indicators to prioritize further investigation and workforce planning. Any intervention should be based on validated records and additional context.