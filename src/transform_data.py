from pathlib import Path
import logging
import pandas as pd
import pandera.pandas as pa


employee_schema = pa.DataFrameSchema(
    {
        "employee_key": pa.Column(
            int,
            nullable=False,
            unique=True,
        ),
        "employee_id": pa.Column(
            str,
            nullable=False,
        ),
        "hire_date": pa.Column(
            pa.DateTime,
            nullable=False,
        ),
        "exit_date": pa.Column(
            pa.DateTime,
            nullable=True,
        ),
            
        "hire_year": pa.Column(
            pa.Int32,
            nullable=False,
        ),

        "tenure_days": pa.Column(
            int,
            nullable=False,
            checks=pa.Check.greater_than_or_equal_to(0),
        ),
    },
    strict=False,
)


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "Data" / "raw"
CLEAN_DIR = BASE_DIR / "Data" / "clean"

CLEAN_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "etl.log", encoding="utf-8"),
        logging.StreamHandler()
    ],
    force=True
)

def transform_employee_data():
    input_file = (
        CLEAN_DIR / "dim_employee_extracted.csv"
    )
     

    if not input_file.exists():
        raise FileNotFoundError(
            f"Extracted employee file not found: {input_file}"
        )

    df = pd.read_csv(input_file)

    rows_before = len(df)
   # Validate unique employee history keys
    if df["employee_key"].isna().any():
        raise ValueError("employee_key contains missing values")

    if df["employee_key"].duplicated().any():
        raise ValueError("Duplicate employee_key values found")

    logging.info("Employee key validation passed")

    # Allow multiple historical records per employee_id,
    # but allow only one current record per employee.
    current_records = df[
        df["is_current"].astype(str).str.strip().str.upper() == "Y"
    ]

    current_counts = current_records.groupby("employee_id").size()
    invalid_current = current_counts[current_counts > 1]

    if not invalid_current.empty:
        raise ValueError(
            "Employees have multiple current records: "
            f"{invalid_current.index.tolist()}"
        )

    logging.info("Current employee record validation passed")
    # Check missing values before cleaning
    missing_report = df.isnull().sum()

    logging.info("Missing values by column:")
    for column, count in missing_report.items():
        logging.info("%s: %s missing values", column, count)

    # Remove duplicate rows
    df = df.drop_duplicates()
    # Preserve valid missing exit dates.
    # Report missing manager IDs for review.
    missing_manager_count = df["manager_id"].isna().sum()

    logging.info(
        "Missing manager_id values requiring review: %s",
        missing_manager_count,
    )

    # Convert date columns to datetime
    date_columns = [
        "date_of_birth",
        "hire_date",
        "exit_date",
        "valid_from",
        "valid_to",
    ]

    for column in date_columns:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce",
        )

    # Check invalid hire and exit date combinations
    invalid_dates = (
        df["exit_date"].notna()
        & (df["hire_date"] > df["exit_date"])
    )

    invalid_count = invalid_dates.sum()

    logging.info(
        "Employees with exit date before hire date: %s",
        invalid_count,
    )

    if invalid_count > 0:
        df_rejected = df.loc[invalid_dates].copy()

        df_rejected["reason"] = "dates out of order"

        REJECTED_DIR = BASE_DIR / "rejected"
        REJECTED_DIR.mkdir(parents=True, exist_ok=True)

        rejected_file = REJECTED_DIR / "employee.csv"

        df_rejected.to_csv(rejected_file, index=False)

        logging.warning(
            "Rejected employee rows saved: %s",
            len(df_rejected),
        )

        df = df.loc[~invalid_dates].copy()
    else:
        logging.info("No invalid employee date records found")
        # Add hire year and tenure
    today = pd.Timestamp.today().normalize()

    df["hire_year"] = df["hire_date"].dt.year

    tenure_end = df["exit_date"].fillna(today)

    df["tenure_days"] = (
        tenure_end - df["hire_date"]
    ).dt.days
    
    # Validate employee data using Pandera
    df = employee_schema.validate(df, lazy=True)

    logging.info("Pandera employee data validation passed")


    # Negative tenure should be flagged, not silently accepted
    negative_tenure = df["tenure_days"] < 0

    if negative_tenure.any():
        raise ValueError(
            "Negative employee tenure found. Review hire/exit dates."
        )

    logging.info("Hire year and tenure columns created")
    # Standardize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Trim extra spaces in text columns
    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].str.strip()

    logging.info("Employee rows before cleaning: %s", rows_before)
    logging.info("Employee rows after cleaning: %s", len(df))
    logging.info("Duplicate rows removed: %s", rows_before - len(df))

    output_file = CLEAN_DIR / "dim_employee_clean.csv"
    df.to_csv(output_file, index=False)
    parquet_file = CLEAN_DIR / "dim_employee_clean.parquet"
    df.to_parquet(parquet_file, index=False)

    logging.info("Employee CSV and Parquet files saved successfully")

    logging.info("Clean employee data saved: %s", output_file)

if __name__ == "__main__":
    transform_employee_data()