import logging
from pathlib import Path

import pandas as pd

# Project folders
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "Data" / "raw"

EXCEL_FILE = (
    RAW_DIR / "03_PulseIQ_Analytics_Star_Schema_Dataset.xlsx"
)

# Required datasets for Task 1
REQUIRED_SHEETS = [
    "dim_employee",
    "fact_payroll",
    "fact_attendance_monthly",
    "fact_leave",
]

# Configure extraction logs
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "etl.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)


def extract_data():
    logging.info("Extraction started")

    if not EXCEL_FILE.exists():
        raise FileNotFoundError(
            f"Excel workbook not found: {EXCEL_FILE}"
        )

    # Read available sheet names
    excel_file = pd.ExcelFile(EXCEL_FILE)
    available_sheets = excel_file.sheet_names

    logging.info("Workbook found: %s", EXCEL_FILE.name)
    logging.info("Available sheets: %s", available_sheets)

    # Check required sheets
    missing_sheets = [
        sheet for sheet in REQUIRED_SHEETS
        if sheet not in available_sheets
    ]

    if missing_sheets:
        raise ValueError(
            f"Required sheets missing: {missing_sheets}"
        )

    extracted_data = {}

    # Extract each required dataset
    for sheet_name in REQUIRED_SHEETS:
        df = pd.read_excel(
            EXCEL_FILE,
            sheet_name=sheet_name,
        )

        extracted_data[sheet_name] = df

        logging.info(
            "Extracted sheet=%s | rows=%s | columns=%s",
            sheet_name,
            len(df),
            len(df.columns),
        )

    logging.info("Extraction completed successfully")
    # Save extracted data for the next ETL step
    OUTPUT_DIR = BASE_DIR / "Data" / "clean"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for sheet_name, df in extracted_data.items():
        output_file = OUTPUT_DIR / f"{sheet_name}_extracted.csv"
        df.to_csv(output_file, index=False)

        logging.info(
            "Saved extracted data | file=%s | rows=%s",
            output_file.name,
            len(df),
        )

    return extracted_data


if __name__ == "__main__":
    data = extract_data()