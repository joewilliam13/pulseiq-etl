# PulseIQ ETL Pipeline

## 1. Project Overview
PulseIQ is an ETL (Extract, Transform, Load) project designed to process employee, payroll, attendance, and leave datasets.

The pipeline extracts data from an Excel workbook, cleans and transforms the datasets, validates data quality, and saves the cleaned data in CSV and Parquet formats.

## 2. Technologies Used
- Python
- Pandas
- Pandera
- OpenPyXL
- PyArrow
- Logging
- Docker

## 3. Project Structure
- `Data/raw/` — Source Excel workbook
- `Data/clean/` — Extracted, cleaned, and rejected datasets
- `src/` — Python ETL scripts
- `logs/` — ETL execution logs
- `requirements.txt` — Python dependencies
- `.env.example` — Environment configuration template
- `Dockerfile` — Docker image configuration

## 4. Datasets Processed
1. Employee
2. Payroll
3. Monthly Attendance
4. Leave

## 5. Data Quality Checks
- Missing-value checks
- Duplicate-row detection
- Date and numeric data validation
- Negative-value checks
- Unique identifier validation
- Leave date-range validation
- Pandera schema validation
- Invalid records saved separately

## 6. Output
The pipeline generates cleaned CSV and Parquet files for the four datasets. Execution logs record row counts, rejected records, validation results, and pipeline status.

## 7. Run the Pipeline
Run the complete pipeline from the project root:

```bash
python src/run_etl.py
```

Docker Compose execution will be documented after the Docker configuration and execution are verified.

### Run with Docker

Build the Docker image:

```bash
docker compose build
```

Run the ETL pipeline:

```bash
docker compose run etl
```

The pipeline extracts, transforms, validates, and saves the cleaned datasets in CSV and Parquet formats.
