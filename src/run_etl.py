
from pathlib import Path
import subprocess
import sys
import logging
from datetime import datetime

# Configure pipeline logging
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
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

pipeline_start = datetime.now()
logging.info("ETL pipeline started at: %s", pipeline_start)
# Project root folder path
BASE_DIR = Path(__file__).resolve().parent.parent

# Source code folder path
SRC_DIR = BASE_DIR / "src"

print("Project folder:", BASE_DIR)
print("Source folder:", SRC_DIR)


# Step 2: Run the extraction script
extract_script = SRC_DIR / "extract_data.py"

print("\nStarting data extraction...")

result = subprocess.run(
    [sys.executable, str(extract_script)],
    cwd=BASE_DIR,
    check=True
)

print("Data extraction completed successfully!")

# Step 3: Transform employee data

employee_script = SRC_DIR / "transform_data.py"

print("\nStarting employee transformation...")

subprocess.run(
    [sys.executable, str(employee_script)],
    cwd=BASE_DIR,
    check=True
)

print("Employee transformation completed successfully!")

# Step 4: Transform payroll data

payroll_script = SRC_DIR / "transform_payroll.py"

print("\nStarting payroll transformation...")

subprocess.run(
    [sys.executable, str(payroll_script)],
    cwd=BASE_DIR,
    check=True
)

print("Payroll transformation completed successfully!")

# Step 5: Transform attendance data

# Step 5: Transform attendance data

attendance_script = SRC_DIR / "transform_attendance.py"

print("\nStarting attendance transformation...")

subprocess.run(
    [sys.executable, str(attendance_script)],
    cwd=BASE_DIR,
    check=True
)

print("Attendance transformation completed successfully!")

# Step 6: Transform leave data

leave_script = SRC_DIR / "transform_leave.py"

print("\nStarting leave transformation...")

subprocess.run(
    [sys.executable, str(leave_script)],
    cwd=BASE_DIR,
    check=True
)

print("Leave transformation completed successfully!")

pipeline_end = datetime.now()

logging.info("ETL pipeline completed at: %s", pipeline_end)

duration = pipeline_end - pipeline_start
logging.info("Total ETL execution time: %s", duration)