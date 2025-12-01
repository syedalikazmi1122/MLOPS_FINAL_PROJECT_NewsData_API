# 🔧 Fix DVC Path Issue and Push to Dagshub

## 🔍 The Problem

DVC is looking in the wrong directory: `C:\Users\hp\data\processed` instead of your project directory.

## 🚀 Solution

### Step 1: Make Sure You're in Project Directory

```powershell
# Navigate to project root
cd "D:\semester 7\mlops\Project\secondtry\MLOPS_FINAL_PROJECT_NewsData_API"

# Verify you're in the right place
Get-Location
# Should show: D:\semester 7\mlops\Project\secondtry\MLOPS_FINAL_PROJECT_NewsData_API
```

### Step 2: Verify DVC is Initialized Here

```powershell
# Check if .dvc folder exists
Test-Path .dvc

# Should return: True
```

### Step 3: Add Data File to DVC

```powershell
# Use full path from project root
python -m dvc add "data\processed\earthquakes_processed_20251129.parquet"

# Or use forward slashes
python -m dvc add data/processed/earthquakes_processed_20251129.parquet
```

### Step 4: Configure Dagshub Remote with Credentials

```powershell
# Make sure dagshub remote has credentials
# Replace YOUR_TOKEN with your actual token
python -m dvc remote modify dagshub --local auth basic
python -m dvc remote modify dagshub --local user i222472
python -m dvc remote modify dagshub --local password YOUR_TOKEN
```

### Step 5: Push to Dagshub

```powershell
# Push to Dagshub (not MinIO)
python -m dvc push dagshub
```

### Step 6: Check Dagshub

1. Go to: **https://dagshub.com/i222472/my-first-repo**
2. Click **"Data" tab**
3. You should see: `data/processed/earthquakes_processed_20251129.parquet`

## 🐛 If DVC Still Has Path Issues

### Option A: Re-initialize DVC in Project Directory

```powershell
# Make sure you're in project root
cd "D:\semester 7\mlops\Project\secondtry\MLOPS_FINAL_PROJECT_NewsData_API"

# Remove old DVC config (backup first if needed)
# Then re-init
python -m dvc init

# Re-add remotes
python -m dvc remote add -d minio-storage s3://earthquake-data
python -m dvc remote modify minio-storage endpointurl http://localhost:9000
python -m dvc remote modify minio-storage access_key_id minioadmin
python -m dvc remote modify minio-storage secret_access_key minioadmin

python -m dvc remote add dagshub https://dagshub.com/i222472/my-first-repo.git
python -m dvc remote modify dagshub --local auth basic
python -m dvc remote modify dagshub --local user i222472
python -m dvc remote modify dagshub --local password YOUR_TOKEN
```

### Option B: Use Absolute Path

```powershell
# Use full absolute path
$filePath = "D:\semester 7\mlops\Project\secondtry\MLOPS_FINAL_PROJECT_NewsData_API\data\processed\earthquakes_processed_20251129.parquet"
python -m dvc add $filePath
```

## 📍 Where Data Appears in Dagshub

After successful push:

1. **Go to**: https://dagshub.com/i222472/my-first-repo
2. **Click "Data" tab** (top navigation)
3. **Navigate to**: `data/processed/`
4. **You'll see**: 
   - `earthquakes_processed_20251129.parquet`
   - File size, version info
   - Download button

## ✅ Quick Test

```powershell
# 1. Make sure you're in project root
cd "D:\semester 7\mlops\Project\secondtry\MLOPS_FINAL_PROJECT_NewsData_API"

# 2. Verify file exists
Test-Path "data\processed\earthquakes_processed_20251129.parquet"

# 3. Add to DVC
python -m dvc add "data\processed\earthquakes_processed_20251129.parquet"

# 4. Push to Dagshub
python -m dvc push dagshub

# 5. Verify
python -m dvc status
```

---

**Try these steps and let me know if you still get path errors!**

