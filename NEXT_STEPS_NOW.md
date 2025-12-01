# 🚀 What to Do Next - Step by Step

## ✅ Script Fixed!

The setup script has been fixed. Now follow these steps:

## Step 1: Run the Setup Script

```powershell
.\setup_dagshub.ps1 -DagshubToken "08e8581ecb0f5ae2401d2acd8156d4765de547e5"
```

This will:
- Configure DVC remote to Dagshub
- Create .env file with MLflow credentials
- Verify configuration

## Step 2: Add .env to .gitignore (Security)

```powershell
# Check if .env is already in .gitignore
Select-String -Path .gitignore -Pattern "\.env"

# If not found, add it
Add-Content .gitignore ".env"
```

## Step 3: Enable MLflow & DVC in Dagshub

1. Go to: **https://dagshub.com/i222472/my-first-repo/settings**
2. Scroll to **"Integrations"** section
3. Enable:
   - ✅ **MLflow**
   - ✅ **DVC**
4. Click **"Save"**

## Step 4: Restart Docker Containers

```powershell
# Set the token as environment variable
$env:DAGSHUB_TOKEN = "08e8581ecb0f5ae2401d2acd8156d4765de547e5"

# Restart containers
docker-compose down
docker-compose up -d
```

## Step 5: Verify Setup

```powershell
# Check DVC remotes
python -m dvc remote list

# Should show:
# dagshub    https://dagshub.com/i222472/my-first-repo.git
# minio-storage   s3://earthquake-data    (default)
```

## Step 6: Run Your DAG

1. **Open Airflow UI**: http://localhost:8080
2. **Find DAG**: `earthquake_etl_pipeline`
3. **Trigger DAG**: Click ▶️ → "Trigger DAG"
4. **Wait for completion** (all tasks should turn green ✅)

## Step 7: Verify in Dagshub

After DAG completes:

1. Go to: **https://dagshub.com/i222472/my-first-repo**
2. Click **"Experiments"** tab
   - Should see MLflow experiment runs
   - Click on a run to see metrics (RMSE, MAE, R²)
   - Check "Artifacts" for profiling reports
3. Click **"Data"** tab
   - Should see DVC-tracked data files
4. Click **"Open MLflow UI"** button
   - See detailed experiment tracking

## ✅ Success Indicators

You'll know it's working when:

- ✅ **Experiments tab** shows training runs with metrics
- ✅ **MLflow UI** shows model artifacts
- ✅ **Artifacts** section has profiling reports (HTML files)
- ✅ **Data tab** shows versioned parquet files
- ✅ **Model Registry** has trained models

## 🎉 Once Verified

**Phase II is 100% complete!**

You now have:
- ✅ All experiments tracked in Dagshub
- ✅ Models in MLflow Model Registry  
- ✅ Profiling reports as MLflow artifacts
- ✅ Data versioned with DVC

## 🐛 Troubleshooting

### If DAG fails with MLflow errors:

```powershell
# Check if .env file exists and has correct content
Get-Content .env

# Should show:
# MLFLOW_TRACKING_URI=https://dagshub.com/i222472/my-first-repo.mlflow
# MLFLOW_TRACKING_USERNAME=i222472
# MLFLOW_TRACKING_PASSWORD=08e8581ecb0f5ae2401d2acd8156d4765de547e5
```

### If DVC push fails:

```powershell
# Check DVC remote configuration
python -m dvc remote list
python -m dvc remote modify dagshub --show

# Test connection
python -m dvc push dagshub
```

### If MLflow can't connect:

- Verify MLflow is enabled in Dagshub settings
- Check token is correct
- Verify tracking URI format is correct

## 📝 Quick Commands Reference

```powershell
# Check DVC status
python -m dvc status

# Push data to Dagshub
python -m dvc push dagshub

# View MLflow experiments locally (if needed)
python -c "import mlflow; mlflow.set_tracking_uri('https://dagshub.com/i222472/my-first-repo.mlflow'); print(mlflow.list_experiments())"
```

---

**Ready? Start with Step 1 above!** 🚀

