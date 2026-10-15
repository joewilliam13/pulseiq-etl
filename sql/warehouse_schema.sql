CREATE SCHEMA IF NOT EXISTS dw;

-- Employee dimension
CREATE TABLE IF NOT EXISTS dw.dim_employee (
    employee_key BIGINT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    full_name TEXT,
    gender TEXT,
    date_of_birth DATE,
    hire_date DATE,
    exit_date DATE,
    employment_status TEXT,
    employment_type TEXT,
    department_id TEXT,
    role_id TEXT,
    role_title TEXT,
    job_level TEXT,
    manager_id TEXT,
    work_location TEXT,
    work_mode TEXT,
    highest_education TEXT,
    valid_from DATE,
    valid_to DATE,
    is_current BOOLEAN,
    change_reason TEXT,
    hire_year INTEGER,
    tenure_days INTEGER
);

-- Department dimension
CREATE TABLE IF NOT EXISTS dw.dim_department (
    department_id TEXT PRIMARY KEY,
    department_name TEXT
);

-- Role dimension
CREATE TABLE IF NOT EXISTS dw.dim_role (
    role_id TEXT PRIMARY KEY,
    role_title TEXT
);

-- Date dimension
CREATE TABLE IF NOT EXISTS dw.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER,
    month INTEGER,
    month_name TEXT,
    quarter INTEGER
);

-- Leave type dimension
CREATE TABLE IF NOT EXISTS dw.dim_leave_type (
    leave_type_code TEXT PRIMARY KEY,
    leave_type_name TEXT
);

-- Attendance fact
CREATE TABLE IF NOT EXISTS dw.fact_attendance_monthly (
    attendance_fact_id BIGINT PRIMARY KEY,
    employee_id TEXT,
    employee_key BIGINT,
    date_key INTEGER,
    department_id TEXT,
    scheduled_days NUMERIC(8,2),
    present_days NUMERIC(8,2),
    wfh_days NUMERIC(8,2),
    half_days_unpaid NUMERIC(8,2),
    paid_leave_days NUMERIC(8,2),
    unpaid_absence_days NUMERIC(8,2),
    late_arrivals INTEGER,
    avg_hours_worked NUMERIC(8,2),
    overtime_hours NUMERIC(8,2),
    attendance_rate NUMERIC(8,2),
    period_end_date DATE
);

-- Payroll fact
CREATE TABLE IF NOT EXISTS dw.fact_payroll (
    payroll_item_id BIGINT PRIMARY KEY,
    run_id TEXT,
    employee_id TEXT,
    date_key INTEGER,
    employee_key BIGINT,
    period_end_date DATE,
    department_id TEXT,
    role_id TEXT,
    payable_days NUMERIC(8,2),
    lop_days NUMERIC(8,2),
    overtime_hours_paid NUMERIC(8,2),
    variable_pay_type TEXT,
    monthly_fixed_gross NUMERIC(18,2),
    basic NUMERIC(18,2),
    hra NUMERIC(18,2),
    conveyance NUMERIC(18,2),
    medical NUMERIC(18,2),
    special_allowance NUMERIC(18,2),
    earned_fixed_pay NUMERIC(18,2),
    overtime_pay NUMERIC(18,2),
    variable_pay NUMERIC(18,2),
    gross_pay NUMERIC(18,2),
    pf_employee NUMERIC(18,2),
    esi_employee NUMERIC(18,2),
    professional_tax NUMERIC(18,2),
    tds NUMERIC(18,2),
    other_deductions NUMERIC(18,2),
    total_deductions NUMERIC(18,2),
    net_pay NUMERIC(18,2),
    pf_employer NUMERIC(18,2),
    esi_employer NUMERIC(18,2),
    employer_cost NUMERIC(18,2),
    headcount_flag INTEGER
);

-- Leave fact
CREATE TABLE IF NOT EXISTS dw.fact_leave (
    leave_request_id BIGINT PRIMARY KEY,
    employee_id TEXT,
    employee_key BIGINT,
    leave_type_code TEXT,
    start_date_key INTEGER,
    end_date_key INTEGER,
    start_date DATE,
    end_date DATE,
    days NUMERIC(8,2),
    status TEXT,
    applied_on DATE,
    decided_on DATE,
    approver_id TEXT,
    reason TEXT,
    start_date_year INTEGER,
    start_date_month INTEGER,
    end_date_year INTEGER,
    end_date_month INTEGER,
    applied_on_year INTEGER,
    applied_on_month INTEGER,
    decided_on_year INTEGER,
    decided_on_month INTEGER
);

-- Monthly headcount fact
CREATE TABLE IF NOT EXISTS dw.fact_headcount_monthly (
    date_key INTEGER,
    department_id TEXT,
    headcount_end INTEGER,
    hires INTEGER DEFAULT 0,
    exits INTEGER DEFAULT 0,
    PRIMARY KEY (date_key, department_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_employee_id
    ON dw.dim_employee (employee_id);

CREATE INDEX IF NOT EXISTS idx_employee_department
    ON dw.dim_employee (department_id);

CREATE INDEX IF NOT EXISTS idx_payroll_employee_key
    ON dw.fact_payroll (employee_key);

CREATE INDEX IF NOT EXISTS idx_payroll_period_end
    ON dw.fact_payroll (period_end_date);

CREATE INDEX IF NOT EXISTS idx_attendance_employee_key
    ON dw.fact_attendance_monthly (employee_key);

CREATE INDEX IF NOT EXISTS idx_attendance_period_end
    ON dw.fact_attendance_monthly (period_end_date);

CREATE INDEX IF NOT EXISTS idx_leave_employee_key
    ON dw.fact_leave (employee_key);

CREATE INDEX IF NOT EXISTS idx_leave_dates
    ON dw.fact_leave (start_date, end_date);

-- Employee dimension relationships
ALTER TABLE dw.dim_employee
ADD CONSTRAINT fk_employee_department
FOREIGN KEY (department_id)
REFERENCES dw.dim_department (department_id);

ALTER TABLE dw.dim_employee
ADD CONSTRAINT fk_employee_role
FOREIGN KEY (role_id)
REFERENCES dw.dim_role (role_id);

-- Payroll relationships
ALTER TABLE dw.fact_payroll
ADD CONSTRAINT fk_payroll_employee
FOREIGN KEY (employee_key)
REFERENCES dw.dim_employee (employee_key);

ALTER TABLE dw.fact_payroll
ADD CONSTRAINT fk_payroll_department
FOREIGN KEY (department_id)
REFERENCES dw.dim_department (department_id);

ALTER TABLE dw.fact_payroll
ADD CONSTRAINT fk_payroll_role
FOREIGN KEY (role_id)
REFERENCES dw.dim_role (role_id);

ALTER TABLE dw.fact_payroll
ADD CONSTRAINT fk_payroll_date
FOREIGN KEY (date_key)
REFERENCES dw.dim_date (date_key);

-- Attendance relationships
ALTER TABLE dw.fact_attendance_monthly
ADD CONSTRAINT fk_attendance_employee
FOREIGN KEY (employee_key)
REFERENCES dw.dim_employee (employee_key);

ALTER TABLE dw.fact_attendance_monthly
ADD CONSTRAINT fk_attendance_department
FOREIGN KEY (department_id)
REFERENCES dw.dim_department (department_id);

ALTER TABLE dw.fact_attendance_monthly
ADD CONSTRAINT fk_attendance_date
FOREIGN KEY (date_key)
REFERENCES dw.dim_date (date_key);

-- Leave relationships
ALTER TABLE dw.fact_leave
ADD CONSTRAINT fk_leave_employee
FOREIGN KEY (employee_key)
REFERENCES dw.dim_employee (employee_key);

ALTER TABLE dw.fact_leave
ADD CONSTRAINT fk_leave_type
FOREIGN KEY (leave_type_code)
REFERENCES dw.dim_leave_type (leave_type_code);

ALTER TABLE dw.fact_leave
ADD CONSTRAINT fk_leave_start_date
FOREIGN KEY (start_date_key)
REFERENCES dw.dim_date (date_key);

ALTER TABLE dw.fact_leave
ADD CONSTRAINT fk_leave_end_date
FOREIGN KEY (end_date_key)
REFERENCES dw.dim_date (date_key);

-- Monthly headcount relationships
ALTER TABLE dw.fact_headcount_monthly
ADD CONSTRAINT fk_headcount_department
FOREIGN KEY (department_id)
REFERENCES dw.dim_department (department_id);

ALTER TABLE dw.fact_headcount_monthly
ADD CONSTRAINT fk_headcount_date
FOREIGN KEY (date_key)
REFERENCES dw.dim_date (date_key);