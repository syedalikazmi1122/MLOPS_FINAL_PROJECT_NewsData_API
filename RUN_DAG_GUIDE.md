# 🚀 Complete Guide: Running the Full Pipeline via Airflow DAG

This guide shows you how to run the **entire MLOps pipeline** from data fetching to model training using the Airflow DAG.

## 📋 Pipeline Overview

The DAG (`dags/earthquake_etl_dag.py`) runs these tasks in sequence:

```
1. Extract Data (USGS API)
   ↓
2. Quality Check (Mandatory Gate - fails if quality < threshold)
   ↓
3. Transform Data (Feature Engineering)
   ↓
4. Upload to MinIO (Object Storage)
   ↓
5. Version with DVC (Push to MinIO)
   ↓
6. Generate Profiling Report (Log to MLflow)
   ↓
7. Train Model (MLflow Tracking)
```

## 🛠️ Prerequisites

Before running the DAG, ensure:

- [x] **MinIO is running** (Docker container)
- [x] **DVC is configured** with MinIO remote
- [x] **Python dependencies installed** (`pip install -r requirements.txt`)
- [x] **Airflow installed** (Python 3.9-3.13)

## 📦 Step 1: Install Apache Airflow

### Option A: Using Docker (Recommended)

```powershell
# Add Airflow to docker-compose.yml (see below)
docker-compose up -d
```

### Option B: Local Installation

```powershell
# Create separate virtual environment for Airflow (Python 3.11)
python -m venv airflow_venv
.\airflow_venv\Scripts\Activate.ps1

# Install Airflow
pip install apache-airflow

# Initialize Airflow database
airflow db init

# Create admin user
airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com --password admin
```

## 🔧 Step 2: Configure Airflow

### Set Airflow Home Directory

```powershell
# Set environment variable (PowerShell)
$env:AIRFLOW_HOME = "D:\semester 7\mlops\Project\secondtry\MLOPS_FINAL_PROJECT_NewsData_API"

# Or create .env file
echo "AIRFLOW_HOME=D:\semester 7\mlops\Project\secondtry\MLOPS_FINAL_PROJECT_NewsData_API" > .env
```

### Configure DAGs Folder

Airflow needs to know where your DAGs are. Create `airflow.cfg` or set:

```powershell
# In PowerShell
$env:AIRFLOW__CORE__DAGS_FOLDER = "D:\semester 7\mlops\Project\secondtry\MLOPS_FINAL_PROJECT_NewsData_API\dags"
```

### Set Python Path

```powershell
$env:PYTHONPATH = "D:\semester 7\mlops\Project\secondtry\MLOPS_FINAL_PROJECT_NewsData_API"
```

## 🐳 Step 3: Docker Compose Setup (Optional but Recommended)

Create or update `docker-compose.yml` to include Airflow:

```yaml
version: '3.8'

services:
  minio:
    image: minio/minio:latest
    container_name: minio
    ports:
      - "9000:9000"   # API endpoint
      - "9001:9001"   # Console UI
    volumes:
      - ./minio-data:/data
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3
    restart: unless-stopped

  # Add Airflow services (optional)
  # See: https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html
```

## 🚀 Step 4: Start Airflow

### If Using Docker Compose:

```powershell
docker-compose up -d
```

### If Using Local Installation:

**Terminal 1 - Start Webserver:**
```powershell
airflow webserver --port 8080
```

**Terminal 2 - Start Scheduler:**
```powershell
airflow scheduler
```

## 🌐 Step 5: Access Airflow UI

1. Open browser: **http://localhost:8080**
2. Login:
   - Username: `admin`
   - Password: `admin` (or what you set)

## ▶️ Step 6: Run the DAG

### Method 1: Via Airflow UI (Recommended)

1. **Find your DAG**: Look for `earthquake_etl_pipeline` in the DAGs list
2. **Toggle it ON**: Click the toggle switch to enable the DAG
3. **Trigger manually**: Click the "Play" button (▶️) → "Trigger DAG"
4. **Monitor progress**: Click on the DAG name to see the graph view
5. **Watch tasks execute**: Tasks will turn green (success) or red (failed)

### Method 2: Via Command Line

```powershell
# Test the DAG (dry run)
airflow dags test earthquake_etl_pipeline 2024-01-01

# Trigger the DAG
airflow dags trigger earthquake_etl_pipeline

# Check DAG status
airflow dags list | Select-String "earthquake"
```

### Method 3: Test Individual Tasks

```powershell
# Test specific task
airflow tasks test earthquake_etl_pipeline extract_data 2024-01-01
airflow tasks test earthquake_etl_pipeline quality_check 2024-01-01
airflow tasks test earthquake_etl_pipeline transform_data 2024-01-01
airflow tasks test earthquake_etl_pipeline upload_to_minio 2024-01-01
airflow tasks test earthquake_etl_pipeline version_data 2024-01-01
airflow tasks test earthquake_etl_pipeline generate_profiling_report 2024-01-01
airflow tasks test earthquake_etl_pipeline train_model 2024-01-01
```

## 📊 Step 7: Monitor Execution

### In Airflow UI:

1. **Graph View**: See task dependencies and status
2. **Tree View**: See historical runs
3. **Logs**: Click on any task → "Log" to see detailed output
4. **XCom**: View data passed between tasks

### Check Outputs:

**MinIO Console:**
- URL: http://localhost:9001
- Check bucket `earthquake-data` for uploaded files

**MLflow UI (if running locally):**
```powershell
mlflow ui
# Open http://localhost:5000
```

**Local Files:**
- Raw data: `data/raw/earthquakes_combined.geojson`
- Processed data: `data/processed/earthquakes_processed_YYYYMMDD.parquet`

## 🔍 Troubleshooting

### DAG Not Appearing

```powershell
# Check DAGs folder is correct
airflow dags list

# Check for syntax errors
python dags/earthquake_etl_dag.py

# Verify Python path
airflow dags list-import-errors
```

### Tasks Failing

**Common Issues:**

1. **MinIO not running:**
   ```powershell
   docker ps | Select-String "minio"
   docker-compose up -d minio
   ```

2. **DVC not configured:**
   ```powershell
   python -m dvc remote list
   # Should show minio-storage
   ```

3. **Python path issues:**
   - Ensure `PROJECT_ROOT` in DAG points to correct directory
   - Check that all scripts are executable

4. **Missing dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

5. **MLflow not configured (for profiling/training):**
   - These tasks will warn but not fail if MLflow isn't set up
   - Set `MLFLOW_TRACKING_URI` environment variable if using Dagshub

### View Detailed Logs

```powershell
# In Airflow UI: Click task → Log
# Or via command line:
airflow tasks logs earthquake_etl_pipeline extract_data 2024-01-01
```

## 🎯 Quick Test Commands

### Test Full Pipeline Manually (Without Airflow)

```powershell
# 1. Extract
python etl/download_historical.py --start-year 2018 --end-year 2020 --combine

# 2. Quality Check
python etl/data_quality_check.py --input data/raw/earthquakes_combined.geojson

# 3. Transform
python etl/transform_data.py --input data/raw/earthquakes_combined.geojson --output data/processed/test.parquet

# 4. Upload to MinIO
python etl/upload_to_minio.py --file data/processed/test.parquet

# 5. Version with DVC
python -m dvc add data/processed/test.parquet
python -m dvc push

# 6. Generate Profiling Report
python etl/generate_profiling_report.py --input data/processed/test.parquet --log-to-mlflow

# 7. Train Model
python train.py --data data/processed/test.parquet --experiment-name test_run
```

## 📅 Schedule Configuration

The DAG is scheduled to run **daily at 2 AM UTC**. To change:

Edit `dags/earthquake_etl_dag.py`:
```python
schedule_interval='0 2 * * *',  # Daily at 2 AM UTC
# Or use:
# schedule_interval='@daily'
# schedule_interval=None  # Manual trigger only
```

## ✅ Success Checklist

After running the DAG, verify:

- [ ] All tasks completed successfully (green in Airflow UI)
- [ ] Raw data file exists: `data/raw/earthquakes_combined.geojson`
- [ ] Processed data exists: `data/processed/earthquakes_processed_*.parquet`
- [ ] Files visible in MinIO Console
- [ ] DVC push successful (check MinIO for DVC files)
- [ ] Profiling report generated (check MLflow artifacts)
- [ ] Model trained and logged to MLflow

## 🎓 Next Steps

After successful DAG run:

1. **Phase II**: Set up Dagshub for MLflow tracking
2. **Phase III**: Configure CI/CD with GitHub Actions
3. **Phase IV**: Add monitoring with Prometheus/Grafana

## 📚 Additional Resources

- [Airflow Documentation](https://airflow.apache.org/docs/)
- [DAG Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [MinIO Integration Guide](MINIO_INTEGRATION_GUIDE.md)

