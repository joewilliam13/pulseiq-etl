
from pathlib import Path
import logging

import pandas as pd
import pandera.pandas as pa


# 1. Set project paths
BASE_DIR = Path(__file__).resolve().parent.parent
CLEAN_DIR = BASE_DIR / "Data" / "clean"
LOG_DIR = BASE_DIR / "logs"

CLEAN_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


# 2. Configure logging
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
logger = logging.getLogger(__name__)


# 3. Read leave dataset
input_file = CLEAN_DIR / "fact_leave_extracted.csv"

if not input_file.exists():
    raise FileNotFoundError(
        f"Leave input file not found: {input_file}"
    )

df = pd.read_csv(input_file)

df.columns = df.columns.str.strip()

rows_before = len(df)

logger.info("Leave transformation started")
logger.info("Input rows: %s", rows_before)
logger.info("Columns: %s", df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())


# 4. Remove exact duplicate rows
duplicate_count = int(df.duplicated().sum())

logger.info("Exact duplicate rows found: %s", duplicate_count)

df = df.drop_duplicates().copy()



# 5. Convert actual date columns only
date_columns = [
    "start_date",
    "end_date",
    "applied_on",
    "decided_on"
]

invalid_date_mask = pd.Series(False, index=df.index)

for column in date_columns:
    if column not in df.columns:
        continue

    original_values = df[column].copy()

    converted_values = pd.to_datetime(
        original_values,
        errors="coerce"
    )

    invalid_values = (
        original_values.notna()
        & converted_values.isna()
    )

    invalid_date_mask |= invalid_values
    df[column] = converted_values

    logger.info(
        "Invalid dates in %s: %s",
        column,
        int(invalid_values.sum())
    )



# 6. Convert numeric columns
numeric_keywords = [
    "days",
    "hours",
    "count",
    "amount",
    "balance"
]

numeric_columns = [
    column for column in df.columns
    if any(
        keyword in column.lower()
        for keyword in numeric_keywords
    )
]

invalid_numeric_mask = pd.Series(False, index=df.index)

for column in numeric_columns:
    original_values = df[column].copy()

    converted_values = pd.to_numeric(
        original_values,
        errors="coerce"
    )

    invalid_numbers = (
        original_values.notna()
        & converted_values.isna()
    )

    invalid_numeric_mask |= invalid_numbers
    df[column] = converted_values

    logger.info(
        "Invalid numeric values in %s: %s",
        column,
        int(invalid_numbers.sum())
    )


# 7. Identify negative values in numeric columns
negative_mask = pd.Series(False, index=df.index)

for column in numeric_columns:
    negative_mask |= df[column].lt(0).fillna(False)

    logger.info(
        "Negative values in %s: %s",
        column,
        int(df[column].lt(0).sum())
    )



# 8. Identify records with invalid dates, numbers,
# negative values, or invalid leave date ranges

invalid_leave_range_mask = (
    df["start_date"].notna()
    & df["end_date"].notna()
    & (df["end_date"] < df["start_date"])
)

logger.info(
    "Invalid leave date ranges: %s",
    int(invalid_leave_range_mask.sum())
)

rejected_mask = (
    invalid_date_mask
    | invalid_numeric_mask
    | negative_mask
    | invalid_leave_range_mask
)
df_rejected = df.loc[rejected_mask].copy()

# Add a reason for each rejected record
df_rejected["reason"] = ""

df_rejected.loc[invalid_date_mask.loc[df_rejected.index], "reason"] += (
    "invalid date; "
)

df_rejected.loc[invalid_numeric_mask.loc[df_rejected.index], "reason"] += (
    "invalid numeric value; "
)

df_rejected.loc[negative_mask.loc[df_rejected.index], "reason"] += (
    "negative leave days; "
)

df_rejected.loc[
    invalid_leave_range_mask.loc[df_rejected.index], "reason"
] += "dates out of order; "

# Save rejected records in the rejected folder
REJECTED_DIR = BASE_DIR / "rejected"
REJECTED_DIR.mkdir(parents=True, exist_ok=True)

rejected_file = REJECTED_DIR / "leave.csv"

if not df_rejected.empty:
    df_rejected.to_csv(rejected_file, index=False)
    logger.warning(
        "Rejected rows saved: %s",
        len(df_rejected)
    )
else:
    logger.info("No invalid leave records found")

# 9. Keep valid records
df_clean = df.loc[~rejected_mask].copy()


# 10. Add month and year for date columns
for column in date_columns:
    if column in df_clean.columns:
        df_clean[f"{column}_year"] = (
            df_clean[column].dt.year.astype("Int64")
        )

        df_clean[f"{column}_month"] = (
            df_clean[column].dt.month.astype("Int64")
        )


# 11. Check missing values
logger.info(
    "Missing values after cleaning: %s",
    df_clean.isnull().sum().to_dict()
)



# 12. Pandera validation
leave_schema = pa.DataFrameSchema(
    columns={
        "leave_request_id": pa.Column(
            str,
            nullable=False,
            unique=True
        ),
        "employee_id": pa.Column(
            str,
            nullable=False
        ),
        "start_date": pa.Column(
            pa.DateTime,
            nullable=False
        ),
        "end_date": pa.Column(
            pa.DateTime,
            nullable=False
        ),
        "days": pa.Column(
            float,
            checks=pa.Check.ge(0),
            nullable=False,
            coerce=True
        ),
    },
    checks=[
        pa.Check(
            lambda df: df["end_date"] >= df["start_date"],
            error="Leave end_date must be on or after start_date"
        )
    ],
    strict=False,
    coerce=False
)

leave_schema.validate(df_clean)
logging.info("Pandera leave validation passed")



# 13. Save cleaned dataset
output_file = CLEAN_DIR / "fact_leave_clean.csv"

df_clean.to_csv(output_file, index=False)

parquet_file = CLEAN_DIR / "fact_leave_clean.parquet"
df_clean.to_parquet(parquet_file, index=False)

logging.info("Leave CSV saved: %s", output_file)
logging.info("Leave Parquet saved: %s", parquet_file)

# 14. Log final results
rows_after = len(df_clean)
rejected_rows = len(df_rejected)

logger.info("Leave validation passed")
logger.info("Rows before cleaning: %s", rows_before)
logger.info("Rows after cleaning: %s", rows_after)
logger.info("Rejected rows: %s", rejected_rows)
logger.info("Clean file saved: %s", output_file)

print("\nLeave transformation completed!")
print("Rows before cleaning:", rows_before)
print("Rows after cleaning:", rows_after)
print("Rejected rows:", rejected_rows)
print("Clean file:", output_file)
