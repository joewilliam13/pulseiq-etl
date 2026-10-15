
from pathlib import Path

import pandas as pd


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_DIR = BASE_DIR / "Data" / "clean"
REJECTED_DIR = BASE_DIR / "rejected"


# -----------------------------
# 1. Clean output files exist
# -----------------------------

def test_employee_clean_file_exists():
    file_path = CLEAN_DIR / "dim_employee_clean.csv"
    assert file_path.exists(), "Employee clean CSV is missing"


def test_payroll_clean_file_exists():
    file_path = CLEAN_DIR / "fact_payroll_clean.csv"
    assert file_path.exists(), "Payroll clean CSV is missing"


def test_attendance_clean_file_exists():
    file_path = CLEAN_DIR / "fact_attendance_monthly_clean.csv"
    assert file_path.exists(), "Attendance clean CSV is missing"


def test_leave_clean_file_exists():
    file_path = CLEAN_DIR / "fact_leave_clean.csv"
    assert file_path.exists(), "Leave clean CSV is missing"


# -----------------------------
# 2. Clean files are not empty
# -----------------------------

def test_clean_files_have_rows():
    files = [
        "dim_employee_clean.csv",
        "fact_payroll_clean.csv",
        "fact_attendance_monthly_clean.csv",
        "fact_leave_clean.csv",
    ]

    for filename in files:
        file_path = CLEAN_DIR / filename

        assert file_path.exists(), f"{filename} is missing"

        df = pd.read_csv(file_path)

        assert not df.empty, f"{filename} has no data"


# -----------------------------
# 3. Employee ID uniqueness
# -----------------------------

def test_employee_keys_are_unique():
    file_path = CLEAN_DIR / "dim_employee_clean.csv"
    df = pd.read_csv(file_path)

    assert "employee_key" in df.columns, (
        "employee_key column is missing"
    )

    assert df["employee_key"].notna().all(), (
        "Null employee_key values found"
    )

    assert df["employee_key"].is_unique, (
        "Duplicate employee_key values found"
    )



# -----------------------------
# 4. Payroll values are non-negative
# -----------------------------

def test_payroll_values_are_non_negative():
    file_path = CLEAN_DIR / "fact_payroll_clean.csv"
    df = pd.read_csv(file_path)

    possible_columns = [
        "gross_pay",
        "net_pay",
        "basic_pay",
        "allowances",
        "deductions",
        "employer_cost",
    ]

    checked_columns = [
        column
        for column in possible_columns
        if column in df.columns
    ]

    assert checked_columns, (
        "No expected payroll amount columns found"
    )

    for column in checked_columns:
        values = pd.to_numeric(df[column], errors="coerce")
        values = values.dropna()

        assert (values >= 0).all(), (
            f"Negative values found in {column}"
        )


# -----------------------------
# 5. Leave rejected rows have reasons
# -----------------------------

def test_rejected_leave_has_reason():
    file_path = REJECTED_DIR / "leave.csv"

    assert file_path.exists(), (
        "Rejected leave CSV is missing"
    )

    df = pd.read_csv(file_path)

    assert "reason" in df.columns, (
        "reason column is missing"
    )

    assert not df.empty, (
        "Rejected leave CSV has no rejected rows"
    )

    assert df["reason"].notna().all(), (
        "Some rejected rows have no reason"
    )

    assert df["reason"].astype(str).str.strip().ne("").all(), (
        "Some rejected rows have an empty reason"
    )


# -----------------------------
# 6. Leave dates are rejected correctly
# -----------------------------

def test_rejected_leave_has_invalid_date_order():
    file_path = REJECTED_DIR / "leave.csv"
    df = pd.read_csv(file_path)

    assert "start_date" in df.columns, (
        "start_date column is missing"
    )

    assert "end_date" in df.columns, (
        "end_date column is missing"
    )

    start_dates = pd.to_datetime(
        df["start_date"], errors="coerce"
    )
    end_dates = pd.to_datetime(
        df["end_date"], errors="coerce"
    )

    invalid_rows = start_dates > end_dates

    assert invalid_rows.any(), (
        "No leave rows with dates out of order were found"
    )


# -----------------------------
# 7. Parquet output files exist
# -----------------------------

def test_clean_parquet_files_exist():
    files = [
        "dim_employee_clean.parquet",
        "fact_payroll_clean.parquet",
        "fact_attendance_monthly_clean.parquet",
        "fact_leave_clean.parquet",
    ]

    for filename in files:
        file_path = CLEAN_DIR / filename

        assert file_path.exists(), (
            f"{filename} is missing"
        )


# -----------------------------
# 8. Parquet files contain data
# -----------------------------

def test_clean_parquet_files_have_rows():
    files = [
        "dim_employee_clean.parquet",
        "fact_payroll_clean.parquet",
        "fact_attendance_monthly_clean.parquet",
        "fact_leave_clean.parquet",
    ]

    for filename in files:
        file_path = CLEAN_DIR / filename

        assert file_path.exists(), (
            f"{filename} is missing"
        )

        df = pd.read_parquet(file_path)

        assert not df.empty, (
            f"{filename} has no data"
        )

