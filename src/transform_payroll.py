
from pathlib import Path
import logging
import pandas as pd
import pandera.pandas as pa


payroll_schema = pa.DataFrameSchema(
    {
        "payroll_item_id": pa.Column(str, nullable=False, unique=True),
        "employee_id": pa.Column(str, nullable=False),
        "period_end_date": pa.Column(pa.DateTime, nullable=False),
        "payable_days": pa.Column(float, checks=pa.Check.greater_than_or_equal_to(0)),
        "gross_pay": pa.Column(float, checks=pa.Check.greater_than_or_equal_to(0)),
        "total_deductions": pa.Column(float, checks=pa.Check.greater_than_or_equal_to(0)),
        "net_pay": pa.Column(float, checks=pa.Check.greater_than_or_equal_to(0)),
        "employer_cost": pa.Column(float, checks=pa.Check.greater_than_or_equal_to(0)),
    },
    strict=False,
)



# Project folder paths
BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_DIR = BASE_DIR / "Data" / "clean"
LOG_DIR = BASE_DIR / "logs"

# Logging setup
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "etl.log", encoding="utf-8"),
        logging.StreamHandler()
    ],
    force=True
)

logging.info("Payroll transformation started")

# Load extracted payroll data
input_file = CLEAN_DIR / "fact_payroll_extracted.csv"

if not input_file.exists():
    raise FileNotFoundError(
        f"Payroll input file not found: {input_file}"
    )

df = pd.read_csv(input_file)

logging.info("Payroll data loaded | rows=%s | columns=%s", len(df), len(df.columns))

# Display column names
logging.info("Payroll columns: %s", df.columns.tolist())

print(df.head())

# Check missing values
logging.info("Missing values by column:")
for column in df.columns:
    missing_count = df[column].isna().sum()
    logging.info("%s: %s missing values", column, missing_count)

# Check duplicate rows
duplicate_count = df.duplicated().sum()
logging.info("Duplicate payroll rows: %s", duplicate_count)

# Record row count before cleaning
rows_before = len(df)
logging.info("Payroll rows before cleaning: %s", rows_before)


# Remove exact duplicate rows
df = df.drop_duplicates()

# Convert date column
df["period_end_date"] = pd.to_datetime(
    df["period_end_date"],
    errors="coerce"
)

# Check invalid dates
invalid_dates = df["period_end_date"].isna()
invalid_date_count = invalid_dates.sum()

logging.info(
    "Invalid period end dates: %s",
    invalid_date_count
)

# Check negative payroll values
pay_columns = [
    "payable_days",
    "lop_days",
    "overtime_hours_paid",
    "monthly_fixed_gross",
    "gross_pay",
    "total_deductions",
    "net_pay",
    "employer_cost",
]

for column in pay_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    negative_count = (df[column] < 0).sum()

    logging.info(
        "Negative values in %s: %s",
        column,
        negative_count
    )

logging.info(
    "Payroll rows after duplicate removal: %s",
    len(df)
)

# Identify invalid payroll records
invalid_dates = df["period_end_date"].isna()

pay_columns = [
    "payable_days",
    "lop_days",
    "overtime_hours_paid",
    "monthly_fixed_gross",
    "gross_pay",
    "total_deductions",
    "net_pay",
    "employer_cost",
]

negative_values = (df[pay_columns] < 0).any(axis=1)

invalid_records = invalid_dates | negative_values


# Save rejected records for review
REJECTED_DIR = BASE_DIR / "rejected"
REJECTED_DIR.mkdir(parents=True, exist_ok=True)

rejected_file = REJECTED_DIR / "payroll.csv"

if invalid_records.any():
    df_rejected = df.loc[invalid_records].copy()

    # Add rejection reason
    df_rejected["reason"] = ""

    df_rejected.loc[
        invalid_dates.loc[df_rejected.index],
        "reason"
    ] += "invalid date; "

    df_rejected.loc[
        negative_values.loc[df_rejected.index],
        "reason"
    ] += "negative payroll value; "

    df_rejected.to_csv(rejected_file, index=False)

    logging.warning(
        "Rejected payroll rows saved: %s",
        len(df_rejected),
    )
else:
    logging.info("No invalid payroll records found")

# Keep only valid payroll records
df_clean = df.loc[~invalid_records].copy()


# Keep only valid payroll records
df_clean = df.loc[~invalid_records].copy()

# Validate payroll data using Pandera
df_clean = payroll_schema.validate(df_clean, lazy=True)

logging.info("Pandera payroll data validation passed")

# Record row counts
rows_after = len(df_clean)
rejected_count = int(invalid_records.sum())

logging.info("Payroll rows before cleaning: %s", rows_before)
logging.info("Payroll rows after cleaning: %s", rows_after)
logging.info("Rejected payroll rows: %s", rejected_count)

# Save clean payroll data
# Save clean payroll data as CSV
output_file = CLEAN_DIR / "fact_payroll_clean.csv"
df_clean.to_csv(output_file, index=False)

# Save clean payroll data as Parquet
parquet_file = CLEAN_DIR / "fact_payroll_clean.parquet"
df_clean.to_parquet(parquet_file, index=False)

logging.info("Payroll CSV saved: %s", output_file)
logging.info("Payroll Parquet saved: %s", parquet_file)