# ⚡ Quick Start: Run Full Pipeline via DAG

## 🎯 What You'll Run

The DAG executes this complete pipeline:

```
1. Extract Data (USGS API)
   ↓
2. Quality Check (Mandatory Gate)
   ↓
3. Transform Data (Feature Engineering)
   ↓
4. Upload to MinIO
   ↓
5. Version with DVC
   ↓
6. Generate Profiling Report (MLflow)
   ↓
7. Train Model (MLflow)
```

## 🚀 Quick Setup (3 Steps)

### Step 1: Ensure Prerequisites

```powershell
# Check MinIO is running
docker ps | Select-String "minio"

# If not running:
docker-compose up -d minio

# Verify DVC is configured
python -m dvc remote list
# Should show: minio-storage
```

### Step 2: Install & Start Airflow

**Option A: Quick Test (No Airflow)**
Skip to "Manual Test" section below.

**Option B: With Airflow**

```powershell
# Install Airflow (in separate venv recommended)
python -m venv airflow_venv
.\airflow_venv\Scripts\Activate.ps1
pip install apache-airflow

# Initialize
airflow db init
airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin

# Set environment
$env:AIRFLOW_HOME = $PWD
$env:PYTHONPATH = $PWD

# Start (in 2 terminals)
# Terminal 1:
airflow webserver --port 8080

# Terminal 2:
airflow scheduler
```

### Step 3: Run the DAG

**Via Airflow UI:**
1. Open http://localhost:8080
2. Login: `admin` / `admin`
3. Find `earthquake_etl_pipeline`
4. Toggle ON → Click ▶️ → "Trigger DAG"
5. Watch it run!

**Via Command Line:**
```powershell
# Trigger DAG
airflow dags trigger earthquake_etl_pipeline

# Or test individual task
airflow tasks test earthquake_etl_pipeline extract_data 2024-01-01
```

## 🧪 Manual Test (Without Airflow)

If you want to test without Airflow setup:

```powershell
# Run each step manually
python etl/download_historical.py --start-year 2018 --end-year 2020 --combine
python etl/data_quality_check.py --input data/raw/earthquakes_combined.geojson
python etl/transform_data.py --input data/raw/earthquakes_combined.geojson --output data/processed/test.parquet
python etl/upload_to_minio.py --file data/processed/test.parquet
python -m dvc add data/processed/test.parquet
python -m dvc push
python etl/generate_profiling_report.py --input data/processed/test.parquet --log-to-mlflow
python train.py --data data/processed/test.parquet --experiment-name test_run
```

## ✅ Verify Success

After DAG completes:

- [ ] **MinIO Console** (http://localhost:9001): Files in `earthquake-data` bucket
- [ ] **Local Files**: `data/processed/earthquakes_processed_*.parquet` exists
- [ ] **MLflow UI** (`mlflow ui`): Model and profiling report logged
- [ ] **Airflow UI**: All tasks green ✅

## 📚 Full Documentation

For detailed setup and troubleshooting, see:
- **[RUN_DAG_GUIDE.md](RUN_DAG_GUIDE.md)** - Complete guide with troubleshooting
- **[MINIO_INTEGRATION_GUIDE.md](MINIO_INTEGRATION_GUIDE.md)** - MinIO setup details

## 🐛 Quick Troubleshooting

**DAG not appearing?**
```powershell
airflow dags list | Select-String "earthquake"
airflow dags list-import-errors
```

**Tasks failing?**
- Check MinIO is running: `docker ps`
- Check DVC config: `python -m dvc remote list`
- View logs in Airflow UI (click task → Log)

**Need help?** See RUN_DAG_GUIDE.md for detailed troubleshooting.

