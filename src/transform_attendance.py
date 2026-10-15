
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


# 3. Read attendance dataset
input_file = CLEAN_DIR / "fact_attendance_monthly_extracted.csv"

if not input_file.exists():
    raise FileNotFoundError(
        f"Attendance input file not found: {input_file}"
    )

df = pd.read_csv(input_file)

rows_before = len(df)

logger.info("Attendance transformation started")
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


# 5. Clean column names
df.columns = df.columns.str.strip()


# 6. Identify date columns and convert them
date_columns = [
    column for column in df.columns
    if "date" in column.lower()
]

invalid_date_mask = pd.Series(False, index=df.index)

for column in date_columns:
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


# 7. Convert numeric columns
numeric_columns = [
    column for column in df.columns
    if any(
        keyword in column.lower()
        for keyword in [
            "days",
            "hours",
            "count",
            "minutes",
            "percentage",
            "percent",
            "rate"
        ]
    )
]

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

    logger.info(
        "Invalid numeric values in %s: %s",
        column,
        int(invalid_numbers.sum())
    )

    df[column] = converted_values


# 8. Identify invalid date records
rejected_mask = invalid_date_mask.copy()

# Negative attendance values are invalid when the column
# represents a count, days, hours, or minutes.
for column in numeric_columns:
    if any(
        keyword in column.lower()
        for keyword in ["days", "hours", "count", "minutes"]
    ):
        rejected_mask |= df[column].lt(0).fillna(False)



# 9. Save rejected records separately
df_rejected = df.loc[rejected_mask].copy()

REJECTED_DIR = BASE_DIR / "rejected"
REJECTED_DIR.mkdir(parents=True, exist_ok=True)

rejected_file = REJECTED_DIR / "attendance.csv"

if not df_rejected.empty:
    # Add rejection reason
    df_rejected["reason"] = ""

    # Identify invalid date values
    df_rejected.loc[
        invalid_date_mask.loc[df_rejected.index],
        "reason"
    ] += "invalid date; "

    # Identify invalid numeric values
    for column in numeric_columns:
        original_values = pd.read_csv(input_file)[column]
        converted_values = pd.to_numeric(
            original_values,
            errors="coerce"
        )

        invalid_numbers = (
            original_values.notna()
            & converted_values.isna()
        )

        matching_indices = df_rejected.index.intersection(
            invalid_numbers.index[invalid_numbers]
        )

        df_rejected.loc[
            matching_indices, "reason"
        ] += f"invalid numeric value in {column}; "

        if any(
            keyword in column.lower()
            for keyword in ["days", "hours", "count", "minutes"]
        ):
            negative_indices = df.index[
                df[column].lt(0).fillna(False)
            ]

            matching_negative = df_rejected.index.intersection(
                negative_indices
            )

            df_rejected.loc[
                matching_negative, "reason"
            ] += f"negative value in {column}; "

    df_rejected.to_csv(rejected_file, index=False)

    logger.warning(
        "Rejected attendance rows saved: %s",
        len(df_rejected)
    )
else:
    logger.info("No invalid attendance records found")
# 10. Keep valid records
df_clean = df.loc[~rejected_mask].copy()


# 11. Check missing values
logger.info(
    "Missing values after basic cleaning: %s",
    df_clean.isnull().sum().to_dict()
)



# 12. Pandera validation
attendance_schema = pa.DataFrameSchema(
    columns={
        "attendance_fact_id": pa.Column(
            str,
            nullable=False,
            unique=True
        ),
        "employee_id": pa.Column(
            str,
            nullable=False
        ),
        "attendance_rate": pa.Column(
            float,
            checks=pa.Check.in_range(0, 1),
            nullable=True,
            coerce=True
        ),
        "scheduled_days": pa.Column(
            float,
            checks=pa.Check.ge(0),
            nullable=True,
            coerce=True
        ),
        "present_days": pa.Column(
            float,
            checks=pa.Check.ge(0),
            nullable=True,
            coerce=True
        ),
    },
    strict=False,
    coerce=False
)

attendance_schema.validate(df_clean)
logging.info("Pandera attendance validation passed")

# 13. Save cleaned attendance dataset
output_file = CLEAN_DIR / "fact_attendance_monthly_clean.csv"
df_clean.to_csv(output_file, index=False)

parquet_file = CLEAN_DIR / "fact_attendance_monthly_clean.parquet"
df_clean.to_parquet(parquet_file, index=False)

logging.info("Attendance CSV saved: %s", output_file)
logging.info("Attendance Parquet saved: %s", parquet_file)


# 14. Log final row counts
rows_after = len(df_clean)
rejected_rows = len(df_rejected)

logger.info("Attendance validation passed")
logger.info("Rows before cleaning: %s", rows_before)
logger.info("Rows after cleaning: %s", rows_after)
logger.info("Rejected rows: %s", rejected_rows)
logger.info("Clean file saved: %s", output_file)

print("\nAttendance transformation completed!")
print("Rows before cleaning:", rows_before)
print("Rows after cleaning:", rows_after)
print("Rejected rows:", rejected_rows)
print("Clean file:", output_file)
