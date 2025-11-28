# MLOps Final Project: Real-Time Predictive System (RPS)

Automated MLOps pipeline for earthquake prediction using time-series data from USGS API.

## Project Overview

This project implements a complete MLOps pipeline following the 4-phase structure:

- **Phase I**: Problem Definition and Data Ingestion ✅
- **Phase II**: Experimentation and Model Management (In Progress)
- **Phase III**: CI/CD Pipeline (Pending)
- **Phase IV**: Monitoring and Observability (Pending)

## Project Structure

```
MLOPS_FINAL_PROJECT_NewsData_API/
├── etl/
│   ├── download_historical.py    # Data extraction from USGS API
│   ├── data_quality_check.py     # Mandatory quality gate
│   └── transform_data.py         # Feature engineering & formatting
├── dags/
│   └── earthquake_etl_dag.py     # Apache Airflow DAG
├── data/
│   ├── raw/                      # Raw GeoJSON data
│   └── processed/                # Processed parquet files
├── requirements.txt
└── README.md
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Manual Data Fetching (Testing)

```bash
# Fetch data for 2018-2020 in 1-year intervals
python etl/download_historical.py --start-year 2018 --end-year 2020 --interval-years 1 --combine

# With custom magnitude threshold
python etl/download_historical.py --start-year 2018 --end-year 2020 --minmagnitude 4.0 --combine
```

### 3. Data Quality Check

```bash
# Check raw GeoJSON data
python etl/data_quality_check.py --input data/raw/earthquakes_combined.geojson --format geojson

# Check processed parquet data
python etl/data_quality_check.py --input data/processed/earthquakes_processed.parquet --format parquet
```

### 4. Transform Data for Training

```bash
python etl/transform_data.py \
    --input data/raw/earthquakes_combined.geojson \
    --output data/processed/earthquakes_processed.parquet
```

## Automated Pipeline (Apache Airflow)

### Setup Airflow

1. Initialize Airflow database:
```bash
airflow db init
```

2. Create admin user:
```bash
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin
```

3. Start Airflow webserver and scheduler:
```bash
# Terminal 1: Webserver
airflow webserver --port 8080

# Terminal 2: Scheduler
airflow scheduler
```

4. Access Airflow UI: http://localhost:8080

### DAG Configuration

The DAG (`dags/earthquake_etl_dag.py`) runs daily at 2 AM UTC and:
- Extracts data from USGS API (2010 to previous year)
- Runs mandatory quality checks (fails if >1% null values)
- Transforms data with feature engineering
- Versions data with DVC

## Data Pipeline Flow

```
USGS API → Extract → Quality Check → Transform → Version (DVC) → Storage
                ↓ (fails if quality < threshold)
            STOP DAG
```

## Features Created

The transformation script creates:

### Time Features
- Year, month, day, hour, day_of_week
- Cyclical encodings (sin/cos) for periodic patterns

### Lag Features
- Time since last earthquake
- Magnitude lags (lag1, lag2, lag3)
- Rolling statistics (24h, 7d, 30d means)
- Rolling counts (earthquake frequency)
- Rolling standard deviations

### Location Features
- Absolute latitude
- Pacific Ring of Fire indicator

## Quality Checks

The mandatory quality gate checks:
- ✅ Row count (minimum 100 rows)
- ✅ Null values (<1% in key columns)
- ✅ Schema validation (required columns, data types)
- ✅ Value ranges (magnitude 0-10, lat/lon ranges)

## Next Steps

1. **Set up DVC remote** (Dagshub/S3/MinIO)
2. **Configure MLflow** with Dagshub
3. **Create training script** (`train.py`)
4. **Set up GitHub Actions** CI/CD
5. **Deploy monitoring** (Prometheus + Grafana)

## Configuration

Edit `dags/earthquake_etl_dag.py` to customize:
- `START_YEAR`: Starting year for data collection
- `END_YEAR`: Ending year (defaults to previous year)
- `INTERVAL_YEARS`: Years per API fetch interval
- `MIN_MAGNITUDE`: Minimum earthquake magnitude filter

## Notes

- Data files are gitignored (use DVC for versioning)
- Airflow DAG requires proper Python environment setup
- Windows-compatible (uses platform detection)

## License

Educational project for MLOps course.

