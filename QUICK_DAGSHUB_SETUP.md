# ⚡ Quick Dagshub Setup (5 Minutes)

Your repository: **https://dagshub.com/i222472/my-first-repo**

## 🚀 Quick Setup Steps

### Step 1: Enable MLflow & DVC in Dagshub (1 minute)

1. Go to: **https://dagshub.com/i222472/my-first-repo/settings**
2. Scroll to **"Integrations"**
3. Enable:
   - ✅ **MLflow**
   - ✅ **DVC**
4. Click **"Save"**

### Step 2: Get Your Access Token (2 minutes)

1. Go to: **https://dagshub.com/i222472/my-first-repo/settings/tokens**
2. Click **"Generate New Token"**
3. Name: "MLOps Project"
4. Scopes: **repo** + **read**
5. Click **"Generate"**
6. **COPY THE TOKEN** (save it somewhere safe!)

### Step 3: Run Setup Script (1 minute)

```powershell
# Run the setup script (replace YOUR_TOKEN with the token you copied)
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

# Add .env to .gitignore
echo ".env" >> .gitignore
```

### Step 4: Restart Docker (1 minute)

```powershell
# Set token as environment variable for Docker
$env:DAGSHUB_TOKEN = "YOUR_TOKEN"

# Restart containers
docker-compose down
docker-compose up -d
```

### Step 5: Test It! (1 minute)

1. **Run your DAG** in Airflow UI
2. **Check Dagshub**: https://dagshub.com/i222472/my-first-repo
   - Click **"Experiments"** tab → See MLflow runs
   - Click **"Data"** tab → See DVC files

## ✅ Done!

Your pipeline now logs everything to Dagshub:
- ✅ Models → MLflow Model Registry
- ✅ Experiments → MLflow Experiments
- ✅ Profiling Reports → MLflow Artifacts
- ✅ Data → DVC Storage

## 🔍 Verify

After DAG runs, check:
- **Experiments tab**: Should show training runs with metrics
- **Data tab**: Should show versioned data files
- **MLflow UI**: Click "Open MLflow UI" to see detailed experiments

## 📚 Full Guide

See **DAGSHUB_SETUP_COMPLETE.md** for detailed instructions and troubleshooting.

