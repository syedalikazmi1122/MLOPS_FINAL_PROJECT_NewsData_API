# ✅ MinIO & DVC Setup Complete - Next Steps

## ✅ What's Done

1. ✅ **MinIO is running** (Docker container is healthy)
2. ✅ **DVC is initialized** and working
3. ✅ **MinIO remote configured** in DVC:
   - Remote name: `minio-storage`
   - Bucket: `earthquake-data`
   - Endpoint: `http://localhost:9000`
   - Credentials: Configured

## 🧪 Test the Setup

### Option 1: Test Direct Upload to MinIO

```powershell
# Test uploading a file directly to MinIO
python etl/upload_to_minio.py --file data/processed/earthquakes_processed.parquet
```

**Expected:** File uploads to `s3://earthquake-data/processed/...`

**Verify:** Check MinIO Console at http://localhost:9001 → Buckets → earthquake-data

### Option 2: Test DVC Push to MinIO

```powershell
# If you have processed data, add it to DVC tracking
python -m dvc add data/processed/earthquakes_processed.parquet

# Push to MinIO
python -m dvc push
```

**Expected:** DVC pushes the file to MinIO remote storage

**Verify:** Check MinIO Console → Files should appear in `earthquake-data/data/processed/`

## 📋 Complete Pipeline Test

If you want to test the full ETL pipeline:

```powershell
# 1. Extract data
python etl/download_historical.py --start-year 2018 --end-year 2020 --combine

# 2. Quality check
python etl/data_quality_check.py --input data/raw/earthquakes_combined.geojson

# 3. Transform
python etl/transform_data.py --input data/raw/earthquakes_combined.geojson --output data/processed/test_$(Get-Date -Format 'yyyyMMdd').parquet

# 4. Upload to MinIO
python etl/upload_to_minio.py --file data/processed/test_*.parquet

# 5. Version with DVC
python -m dvc add data/processed/test_*.parquet
python -m dvc push
```

## 🚀 What's Next (Project Phases)

### Phase I - ✅ COMPLETE
- ✅ Data extraction
- ✅ Data quality checks
- ✅ Data transformation
- ✅ **MinIO storage integration**
- ✅ **DVC versioning with MinIO**

### Phase II - Next Priority
1. **Set up Dagshub** for MLflow tracking
2. **Test training script** with MLflow
3. **Generate profiling reports** and log to MLflow
4. **Integrate profiling** into Airflow DAG

### Phase III - CI/CD
1. Set up GitHub Actions workflows
2. Configure branching strategy (dev → test → master)
3. Add CML for model comparison
4. Docker containerization for model serving

### Phase IV - Monitoring
1. Add Prometheus metrics to FastAPI
2. Set up Grafana dashboards
3. Configure alerts

## 📝 Quick Reference

### MinIO Console
- URL: http://localhost:9001
- Login: `minioadmin` / `minioadmin`
- Bucket: `earthquake-data`

### DVC Commands
```powershell
# Check status
python -m dvc status

# Add file to tracking
python -m dvc add <file>

# Push to MinIO
python -m dvc push

# Pull from MinIO
python -m dvc pull

# List remotes
python -m dvc remote list
```

### MinIO Upload
```powershell
# Upload file
python etl/upload_to_minio.py --file <path-to-file>

# With custom bucket
python etl/upload_to_minio.py --file <path> --bucket <bucket-name>
```

## ✅ Verification Checklist

- [x] MinIO container running
- [x] MinIO Console accessible
- [x] Bucket `earthquake-data` created
- [x] DVC initialized
- [x] DVC remote configured
- [ ] Test upload successful (run test commands above)
- [ ] Test DVC push successful

## 🎯 Recommended Next Action

**Option 1: Quick Test (Manual)**
```powershell
# Quick test - upload existing processed data
python etl/upload_to_minio.py --file data/processed/earthquakes_processed.parquet
```
Then check MinIO Console to verify the file appears!

**Option 2: Full Pipeline Test (Via Airflow DAG)**
See **[RUN_DAG_GUIDE.md](RUN_DAG_GUIDE.md)** for complete instructions on running the entire pipeline (Extract → Quality Check → Transform → Upload → Version → Profiling → Training) via Airflow DAG.

The DAG now includes:
- ✅ Data extraction
- ✅ Quality checks
- ✅ Data transformation
- ✅ MinIO upload
- ✅ DVC versioning
- ✅ **Profiling report generation** (new)
- ✅ **Model training** (new)

