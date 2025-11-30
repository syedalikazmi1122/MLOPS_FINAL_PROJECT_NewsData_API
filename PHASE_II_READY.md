# ✅ Phase II Setup - Ready to Configure!

## 🎉 What I've Done For You

1. ✅ **Updated docker-compose.yml**
   - Added MLflow tracking URI: `https://dagshub.com/i222472/my-first-repo.mlflow`
   - Added MLflow credentials (username + password/token)
   - Both webserver and scheduler will use Dagshub

2. ✅ **Updated train.py**
   - Now handles Dagshub authentication automatically
   - Reads credentials from environment variables

3. ✅ **Updated generate_profiling_report.py**
   - Now handles Dagshub authentication
   - Will log reports to Dagshub MLflow

4. ✅ **Created setup script**: `setup_dagshub.ps1`
   - Automates DVC and MLflow configuration

5. ✅ **Created guides**:
   - `QUICK_DAGSHUB_SETUP.md` - 5-minute quick start
   - `DAGSHUB_SETUP_COMPLETE.md` - Complete guide
   - `START_PHASE_II.md` - Step-by-step instructions

## 🚀 What You Need to Do (5 Minutes)

### Step 1: Enable MLflow & DVC in Dagshub

Go to: **https://dagshub.com/i222472/my-first-repo/settings**

1. Scroll to **"Integrations"** section
2. Enable:
   - ✅ **MLflow**
   - ✅ **DVC**
3. Click **"Save"**

### Step 2: Get Your Access Token

Go to: **https://dagshub.com/i222472/my-first-repo/settings/tokens**

1. Click **"Generate New Token"**
2. Name: "MLOps Project"
3. Scopes: Select **repo** and **read**
4. Click **"Generate"**
5. **COPY THE TOKEN** (save it - you won't see it again!)

### Step 3: Run Setup Script

```powershell
# Replace YOUR_TOKEN with the actual token you copied
.\setup_dagshub.ps1 -DagshubToken "YOUR_TOKEN"
```

**Or manually:**

```powershell
# Configure DVC
python -m dvc remote add dagshub https://dagshub.com/i222472/my-first-repo.git
python -m dvc remote modify dagshub --local auth basic
python -m dvc remote modify dagshub --local user i222472
python -m dvc remote modify dagshub --local password YOUR_TOKEN

# Create .env file
@"
MLFLOW_TRACKING_URI=https://dagshub.com/i222472/my-first-repo.mlflow
MLFLOW_TRACKING_USERNAME=i222472
MLFLOW_TRACKING_PASSWORD=YOUR_TOKEN
"@ | Out-File -FilePath .env -Encoding utf8
```

### Step 4: Restart Docker Containers

```powershell
# Set token for Docker
$env:DAGSHUB_TOKEN = "YOUR_TOKEN"

# Restart
docker-compose down
docker-compose up -d
```

### Step 5: Test It!

1. **Run your DAG** in Airflow UI (http://localhost:8080)
2. **Check Dagshub**: https://dagshub.com/i222472/my-first-repo
   - Click **"Experiments"** → See MLflow runs
   - Click **"Data"** → See DVC files
   - Click **"Open MLflow UI"** → Detailed experiment view

## ✅ Verification Checklist

After DAG runs:

- [ ] **Experiments tab** shows training runs
- [ ] **MLflow UI** shows metrics (RMSE, MAE, R²)
- [ ] **Model Registry** has trained models
- [ ] **Artifacts** section has profiling reports
- [ ] **Data tab** shows versioned files

## 🎯 Once Verified

**Phase II is 100% complete!** 🎉

You'll have:
- ✅ All experiments tracked in Dagshub
- ✅ Models in MLflow Model Registry
- ✅ Profiling reports as artifacts
- ✅ Data versioned with DVC

Then you can move to **Phase III: CI/CD** when ready!

## 📚 Need Help?

- **Quick Guide**: `QUICK_DAGSHUB_SETUP.md`
- **Complete Guide**: `DAGSHUB_SETUP_COMPLETE.md`
- **Troubleshooting**: See complete guide

