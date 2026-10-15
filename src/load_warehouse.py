import pandas as pd
import psycopg2
from pathlib import Path
from psycopg2.extras import execute_values

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "pulseiq",
    "user": "pulseiq_user",
    "password": "pulseiq_dev_password",
}

BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_DIR = BASE_DIR / "Data" / "clean"
RAW_FILE = (
    BASE_DIR / "Data" / "raw"
    / "03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx"
)


def upsert_dataframe(df, table_name, primary_keys):
    df = df.astype(object).where(pd.notna(df), None)

    columns = list(df.columns)
    column_sql = ", ".join(columns)
    conflict_sql = ", ".join(primary_keys)

    update_columns = [
        col for col in columns if col not in primary_keys
    ]

    if update_columns:
        update_sql = ", ".join(
            f"{col} = EXCLUDED.{col}"
            for col in update_columns
        )
        conflict_action = f"DO UPDATE SET {update_sql}"
    else:
        conflict_action = "DO NOTHING"

    query = f"""
        INSERT INTO dw.{table_name} ({column_sql})
        VALUES %s
        ON CONFLICT ({conflict_sql})
        {conflict_action}
    """

    rows = list(df.itertuples(index=False, name=None))

    if not rows:
        print(f"{table_name}: no rows to load")
        return

    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            execute_values(cur, query, rows, page_size=500)

    print(f"{table_name}: {len(df)} rows processed")


def load_csv_to_table(filename, table_name, primary_keys):
    df = pd.read_csv(CLEAN_DIR / filename, dtype=str)
    upsert_dataframe(df, table_name, primary_keys)


def load_excel_sheet(
    sheet_name, table_name, columns, primary_keys
):
    df = pd.read_excel(RAW_FILE, sheet_name=sheet_name)

    if sheet_name == "dim_date":
        df = df.rename(columns={"date": "full_date"})

    df = df[columns].copy()

    if "date_key" in df.columns:
        df["date_key"] = pd.to_numeric(
            df["date_key"], errors="raise"
        ).astype("int64")

    upsert_dataframe(df, table_name, primary_keys)

if __name__ == "__main__":

    # Clean CSV files
    load_csv_to_table(
        "dim_employee_clean.csv",
        "dim_employee",
        ["employee_key"],
    )

    load_csv_to_table(
        "fact_payroll_clean.csv",
        "fact_payroll",
        ["payroll_item_id"],
    )

    load_csv_to_table(
        "fact_attendance_monthly_clean.csv",
        "fact_attendance_monthly",
        ["attendance_fact_id"],
    )

    load_csv_to_table(
        "fact_leave_clean.csv",
        "fact_leave",
        ["leave_request_id"],
    )

    # Dimension tables from Excel
    load_excel_sheet(
        "dim_department",
        "dim_department",
        ["department_id", "department_name"],
        ["department_id"],
    )

    load_excel_sheet(
        "dim_role",
        "dim_role",
        ["role_id", "role_title"],
        ["role_id"],
    )

    load_excel_sheet(
        "dim_leave_type",
        "dim_leave_type",
        ["leave_type_code", "leave_type_name"],
        ["leave_type_code"],
    )

    load_excel_sheet(
    "dim_date",
    "dim_date",
    [
        "date_key",
        "full_date",
        "year",
        "month_name",
        "quarter",
    ],
    ["date_key"],
)

    # Monthly headcount fact
    load_excel_sheet(
        "fact_headcount_monthly",
        "fact_headcount_monthly",
        [
            "date_key",
            "department_id",
            "headcount_end",
            "hires",
            "exits",
        ],
        ["date_key", "department_id"],
    )