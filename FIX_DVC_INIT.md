# Fix DVC Initialization Issue

## Problem
You're getting: `ERROR: configuration error - config file error: Not inside a DVC repo`

## Solution

### Step 1: Make sure you're in the project directory

```powershell
cd "D:\semester 7\mlops\Project\secondtry\MLOPS_FINAL_PROJECT_NewsData_API"
```

### Step 2: Check if Git is initialized

DVC requires Git to be initialized first:

```powershell
# Check if .git exists
Test-Path .git

# If it doesn't exist, initialize Git:
git init
```

### Step 3: Initialize DVC

```powershell
# If .dvc directory doesn't exist, initialize:
python -m dvc init

# If .dvc exists but DVC still doesn't work, try:
python -m dvc init --force
```

### Step 4: Now add the MinIO remote

```powershell
python -m dvc remote add -d minio-storage s3://earthquake-data
python -m dvc remote modify minio-storage endpointurl http://localhost:9000
python -m dvc remote modify minio-storage access_key_id minioadmin
python -m dvc remote modify minio-storage secret_access_key minioadmin
```

## Quick Fix (All in One)

Run these commands in order:

```powershell
# Navigate to project
cd "D:\semester 7\mlops\Project\secondtry\MLOPS_FINAL_PROJECT_NewsData_API"

# Initialize Git (if not already done)
git init

# Initialize DVC (or force re-init if needed)
python -m dvc init --force

# Add MinIO remote
python -m dvc remote add -d minio-storage s3://earthquake-data
python -m dvc remote modify minio-storage endpointurl http://localhost:9000
python -m dvc remote modify minio-storage access_key_id minioadmin
python -m dvc remote modify minio-storage secret_access_key minioadmin

# Verify
python -m dvc remote list
```

## Important Notes

1. **Port Fix**: I've fixed the endpoint port in `upload_to_minio.py`:
   - ✅ Port **9000** = API endpoint (for S3 operations) - **CORRECT**
   - ❌ Port **9001** = Web console only - **WRONG for API**

2. **DVC requires Git**: DVC needs Git to be initialized in the same directory

3. **Verify you're in the right directory**: Make sure you're in the project root, not your home directory

## Verify Setup

After running the commands above, verify everything works:

```powershell
# Check DVC status
python -m dvc status

# Check remote configuration
python -m dvc remote list

# Test with a file (if you have processed data)
python -m dvc add data/processed/earthquakes_processed.parquet
python -m dvc push
```

