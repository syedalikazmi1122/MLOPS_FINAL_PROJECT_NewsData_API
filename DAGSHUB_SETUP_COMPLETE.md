# 🚀 Dagshub Setup - Complete Configuration Guide

Your Dagshub repository: **https://dagshub.com/i222472/my-first-repo**

## ✅ What's Already Configured

1. ✅ **MLflow Tracking URI** added to docker-compose.yml
   - Set to: `https://dagshub.com/i222472/my-first-repo.mlflow`
   - Will be used by Airflow containers automatically

2. ✅ **DAG configured** to use MLflow for profiling and training

## 🔧 Step-by-Step Setup (15 minutes)

### Step 1: Enable MLflow & DVC in Dagshub (2 minutes)

1. Go to: **https://dagshub.com/i222472/my-first-repo/settings**
2. Scroll to **"Integrations"** section
3. Enable:
   - ✅ **MLflow** (for experiment tracking)
   - ✅ **DVC** (for data versioning)
4. Click **"Save"**

### Step 2: Get Dagshub Access Token (3 minutes)

1. Go to: **https://dagshub.com/i222472/my-first-repo/settings/tokens**
2. Click **"Generate New Token"**
3. Give it a name (e.g., "MLOps Project")
4. Select scopes: **repo** and **read**
5. Click **"Generate Token"**
6. **COPY THE TOKEN** (you won't see it again!)
   - It looks like: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

### Step 3: Configure DVC Remote to Dagshub (5 minutes)

Run these commands in PowerShell:

```powershell
# Make sure you're in the project directory
cd "D:\semester 7\mlops\Project\secondtry\MLOPS_FINAL_PROJECT_NewsData_API"

# Add Dagshub as DVC remote (if not already added)
python -m dvc remote add dagshub https://dagshub.com/i222472/my-first-repo.git

# Configure authentication (replace YOUR_TOKEN with the token you copied)
python -m dvc remote modify dagshub --local auth basic
python -m dvc remote modify dagshub --local user i222472
python -m dvc remote modify dagshub --local password YOUR_TOKEN

# Set as default remote (optional - you can keep MinIO as default)
# python -m dvc remote default dagshub

# Verify configuration
python -m dvc remote list
```

**Note**: Replace `YOUR_TOKEN` with the actual token you copied from Step 2.

### Step 4: Set MLflow Credentials for Dagshub (5 minutes)

Dagshub MLflow requires authentication. Create a `.env` file or set environment variables:

**Option A: Create .env file (Recommended)**

Create `.env` file in project root:

```powershell
# Create .env file
@"
MLFLOW_TRACKING_URI=https://dagshub.com/i222472/my-first-repo.mlflow
MLFLOW_TRACKING_USERNAME=i222472
MLFLOW_TRACKING_PASSWORD=YOUR_TOKEN
"@ | Out-File -FilePath .env -Encoding utf8
```

**Option B: Set in PowerShell (for testing)**

```powershell
$env:MLFLOW_TRACKING_URI = "https://dagshub.com/i222472/my-first-repo.mlflow"
$env:MLFLOW_TRACKING_USERNAME = "i222472"
$env:MLFLOW_TRACKING_PASSWORD = "YOUR_TOKEN"
```

**Important**: Replace `YOUR_TOKEN` with your actual Dagshub token from Step 2.

### Step 5: Update Docker Compose with Credentials

We need to add MLflow credentials to docker-compose.yml. I'll create an updated version.

### Step 6: Restart Docker Containers

```powershell
# Restart to pick up new environment variables
docker-compose down
docker-compose up -d
```

### Step 7: Test the Integration

```powershell
# Test MLflow connection (from your local machine, not Docker)
python -c "import mlflow; mlflow.set_tracking_uri('https://dagshub.com/i222472/my-first-repo.mlflow'); print('Connected!')"

# Or test by running a training locally
python train.py --data data/processed/earthquakes_processed.parquet --experiment-name dagshub_test
```

## ✅ Verification Checklist

After setup, verify:

- [ ] MLflow enabled in Dagshub repo settings
- [ ] DVC enabled in Dagshub repo settings
- [ ] Access token generated and saved
- [ ] DVC remote configured with credentials
- [ ] MLflow credentials set (in .env or environment)
- [ ] Docker containers restarted
- [ ] Test run completed successfully

## 🔍 Verify in Dagshub UI

After running your DAG:

1. Go to: **https://dagshub.com/i222472/my-first-repo**
2. Click **"Experiments"** tab
3. You should see:
   - MLflow experiment runs
   - Model artifacts
   - Profiling reports
   - Training metrics

4. Click **"Data"** tab
5. You should see:
   - DVC-tracked data files
   - Data versions

## 🐛 Troubleshooting

### MLflow Connection Issues

**Error: "401 Unauthorized"**
- Check MLflow credentials are set correctly
- Verify token is valid (not expired)
- Check username matches your Dagshub username

**Error: "Connection refused"**
- Verify MLflow is enabled in Dagshub repo settings
- Check tracking URI format: `https://dagshub.com/username/repo.mlflow`

### DVC Push Issues

**Error: "Authentication failed"**
- Verify DVC remote credentials
- Check token has correct permissions
- Try regenerating token

**Error: "Remote not found"**
- Run: `python -m dvc remote list` to verify
- Re-add remote if needed

## 📝 Quick Reference

### MLflow Tracking URI
```
https://dagshub.com/i222472/my-first-repo.mlflow
```

### DVC Remote
```
https://dagshub.com/i222472/my-first-repo.git
```

### Dagshub Repository
```
https://dagshub.com/i222472/my-first-repo
```

## 🎯 Next Steps After Setup

1. **Run your DAG** in Airflow
2. **Check Dagshub** for logged experiments
3. **Verify** profiling reports appear in MLflow artifacts
4. **Confirm** models are in Model Registry

Once verified, **Phase II is complete!** 🎉

