# Next Steps - MLOps Pipeline Progress

## ✅ Completed (Phase I - Mostly Done)

1. **Data Extraction** ✅
   - Interval-based fetching from USGS API
   - Automatic date range handling
   - Windows-compatible

2. **Data Transformation** ✅
   - Feature engineering (42 features)
   - Time-series features
   - Lag features and rolling statistics
   - Location features

3. **Data Quality Checks** ✅
   - Mandatory quality gate
   - Null value checks (<1% threshold)
   - Schema validation
   - Value range validation

4. **Airflow DAG** ✅
   - Automated pipeline structure
   - Quality gate integration
   - Ready to deploy (needs Python 3.9-3.13)

5. **Training Script** ✅
   - MLflow integration
   - Multiple model types
   - Experiment tracking
   - Model registry

6. **Profiling Report Script** ✅
   - ydata-profiling integration
   - MLflow artifact logging

## 🚧 Next Steps (Priority Order)

### 1. Test Training Script (IMMEDIATE)

```bash
# Test with your processed data
python train.py --data data/processed/earthquakes_processed.parquet --experiment-name test_run

# Try different models
python train.py --data data/processed/earthquakes_processed.parquet --model-type gradient_boosting --n-estimators 200
```

**Expected Output:**
- MLflow run created locally
- Model saved to MLflow
- Metrics logged (RMSE, MAE, R²)

### 2. Set Up Dagshub Integration (Phase II)

1. **Create Dagshub Account:**
   - Go to https://dagshub.com
   - Create account and repository

2. **Configure MLflow Tracking:**
   ```bash
   # Set environment variable
   export MLFLOW_TRACKING_URI="https://dagshub.com/<username>/<repo>.mlflow"
   
   # Or create .env file
   echo "MLFLOW_TRACKING_URI=https://dagshub.com/<username>/<repo>.mlflow" > .env
   ```

3. **Configure DVC Remote:**
   ```bash
   # Initialize DVC
   dvc init
   
   # Add remote (Dagshub)
   dvc remote add origin https://dagshub.com/<username>/<repo>.git
   dvc remote modify origin --local auth basic
   dvc remote modify origin --local user <username>
   dvc remote modify origin --local password <token>
   ```

4. **Test Integration:**
   ```bash
   # Run training (will log to Dagshub)
   python train.py --data data/processed/earthquakes_processed.parquet
   
   # Generate and log profiling report
   python etl/generate_profiling_report.py --input data/processed/earthquakes_processed.parquet --log-to-mlflow
   ```

### 3. Set Up DVC for Data Versioning

```bash
# Initialize DVC
dvc init

# Add processed data to DVC
dvc add data/processed/earthquakes_processed.parquet

# Commit DVC metadata
git add data/processed/earthquakes_processed.parquet.dvc .gitignore
git commit -m "Add processed data to DVC"

# Push to remote (after configuring remote)
dvc push
```

### 4. Update Airflow DAG (When Ready)

1. **Install Airflow** (requires Python 3.9-3.13):
   ```bash
   # Option 1: Use Docker
   docker-compose up airflow-init
   docker-compose up
   
   # Option 2: Use Python 3.12 virtual environment
   python3.12 -m venv airflow_venv
   source airflow_venv/bin/activate  # or airflow_venv\Scripts\activate on Windows
   pip install apache-airflow
   ```

2. **Configure DAG:**
   - Update `dags/earthquake_etl_dag.py` with your paths
   - Set environment variables for MLflow/DVC

3. **Test DAG:**
   ```bash
   airflow dags test earthquake_etl_pipeline
   ```

### 5. Phase III: CI/CD Setup

1. **GitHub Actions Workflow:**
   - Create `.github/workflows/ci.yml`
   - Set up branching strategy (dev → test → master)
   - Add CML integration for model comparison

2. **Docker Containerization:**
   - Create `Dockerfile` for model serving
   - Create `app.py` (FastAPI service)
   - Set up container registry

### 6. Phase IV: Monitoring

1. **Prometheus Integration:**
   - Add Prometheus metrics to FastAPI
   - Expose `/metrics` endpoint

2. **Grafana Dashboard:**
   - Create dashboard for model metrics
   - Set up alerts for drift/latency

## Quick Test Commands

```bash
# 1. Test full pipeline manually
python etl/download_historical.py --start-year 2018 --end-year 2020 --interval-years 1 --combine
python etl/data_quality_check.py --input data/raw/earthquakes_combined.geojson
python etl/transform_data.py --input data/raw/earthquakes_combined.geojson --output data/processed/test.parquet
python etl/data_quality_check.py --input data/processed/test.parquet --format parquet

# 2. Test training
python train.py --data data/processed/earthquakes_processed.parquet --experiment-name test

# 3. Test profiling
python etl/generate_profiling_report.py --input data/processed/earthquakes_processed.parquet --output report.html

# 4. View MLflow UI (if running locally)
mlflow ui
# Then open http://localhost:5000
```

## Current Status Summary

- ✅ **Phase I**: 90% Complete (missing: DVC remote setup, profiling report integration)
- 🚧 **Phase II**: 50% Complete (training script ready, needs Dagshub setup)
- ⏳ **Phase III**: 0% Complete (CI/CD pending)
- ⏳ **Phase IV**: 0% Complete (Monitoring pending)

## Recommended Next Action

**Start with testing the training script** - this will validate your data pipeline and give you a working model:

```bash
python train.py --data data/processed/earthquakes_processed.parquet
```

Then check MLflow UI:
```bash
mlflow ui
# Open http://localhost:5000 in browser
```

This will show you:
- All experiment runs
- Model performance metrics
- Feature importance
- Model artifacts

