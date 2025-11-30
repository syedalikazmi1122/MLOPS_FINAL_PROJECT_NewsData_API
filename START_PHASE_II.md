# 🚀 Start Phase II - Dagshub Integration

## ✅ What's Already Done

1. ✅ Docker-compose.yml updated with MLflow tracking URI
2. ✅ Scripts updated to handle Dagshub authentication
3. ✅ Setup script created (`setup_dagshub.ps1`)

## 🎯 Quick Start (5 Steps)

### Step 1: Enable MLflow & DVC in Dagshub

1. Go to: **https://dagshub.com/i222472/my-first-repo/settings**
2. Find **"Integrations"** section
3. Enable:
   - ✅ **MLflow**
   - ✅ **DVC**
4. Click **"Save"**

### Step 2: Get Access Token

1. Go to: **https://dagshub.com/i222472/my-first-repo/settings/tokens**
2. Click **"Generate New Token"**
3. Name: "MLOps Project"
4. Scopes: **repo** + **read**
5. **Copy the token** (you'll need it!)

### Step 3: Run Setup Script

```powershell
# Replace YOUR_TOKEN with the token you copied
.\setup_dagshub.ps1 -DagshubToken "YOUR_TOKEN"
```

This will:
- Configure DVC remote to Dagshub
- Create .env file with MLflow credentials
- Verify configuration

### Step 4: Restart Docker with Token

```powershell
# Set token as environment variable
$env:DAGSHUB_TOKEN = "YOUR_TOKEN"

# Restart containers
docker-compose down
docker-compose up -d
```

### Step 5: Run Your DAG & Verify

1. **Trigger DAG** in Airflow UI
2. **Check Dagshub**: https://dagshub.com/i222472/my-first-repo
   - **Experiments** tab → MLflow runs
   - **Data** tab → DVC files

## ✅ Success Indicators

After DAG runs, you should see in Dagshub:

- ✅ **Experiments tab**: Training runs with metrics (RMSE, MAE, R²)
- ✅ **MLflow UI**: Click "Open MLflow UI" → See detailed experiments
- ✅ **Model Registry**: Trained models
- ✅ **Artifacts**: Profiling reports
- ✅ **Data tab**: Versioned data files

## 📚 Documentation

- **Quick Setup**: `QUICK_DAGSHUB_SETUP.md`
- **Complete Guide**: `DAGSHUB_SETUP_COMPLETE.md`
- **Troubleshooting**: See complete guide

## 🎉 Once Verified

**Phase II is complete!** You can then move to Phase III (CI/CD).

