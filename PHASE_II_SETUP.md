# Phase II Setup Guide: Dagshub & DVC Integration

## Current Status ✅
- ✅ Training script working
- ✅ MLflow tracking locally
- ✅ Data transformation complete

## Next Steps (Priority Order)

### Step 1: Set Up DVC Locally (No Account Needed)

```powershell
# Install DVC if not already installed
pip install dvc[s3]

# Initialize DVC
dvc init

# Add your processed data to DVC
dvc add data/processed/earthquakes_processed.parquet

# Commit DVC metadata to git
git add data/processed/earthquakes_processed.parquet.dvc .gitignore
git commit -m "Add processed data to DVC"
```

**What this does:**
- Creates `.dvc` directory for tracking
- Creates `.dvc` file that points to your data (small metadata file)
- Updates `.gitignore` to exclude large data files
- Only small metadata files go to git, large data stays local

### Step 2: Create Dagshub Account & Repository

1. **Go to https://dagshub.com**
2. **Sign up** (free account)
3. **Create a new repository:**
   - Click "New Repository"
   - Name it (e.g., `earthquake-mlops`)
   - Choose public or private
   - **Important:** Enable DVC and MLflow in repository settings

### Step 3: Configure Dagshub Integration

#### 3.1 Configure MLflow Tracking

**Option A: Environment Variable (Recommended)**
```powershell
# Windows PowerShell
$env:MLFLOW_TRACKING_URI="https://dagshub.com/<username>/<repo-name>.mlflow"

# Or create .env file (use python-dotenv)
echo "MLFLOW_TRACKING_URI=https://dagshub.com/<username>/<repo-name>.mlflow" > .env
```

**Option B: Direct in Code**
Edit `train.py` and add at the top of `main()`:
```python
mlflow.set_tracking_uri("https://dagshub.com/<username>/<repo-name>.mlflow")
```

#### 3.2 Configure DVC Remote

**Option A: MinIO (Recommended - Free, Local)**
```powershell
# First, set up MinIO (see setup_minio.md or run setup_minio_quick.ps1)
# Then configure DVC:
dvc remote add -d minio-storage s3://earthquake-data
dvc remote modify minio-storage endpointurl http://localhost:9000
dvc remote modify minio-storage access_key_id minioadmin
dvc remote modify minio-storage secret_access_key minioadmin
```

**Option B: Dagshub (Cloud-based)**
```powershell
# Add Dagshub as DVC remote
dvc remote add origin https://dagshub.com/<username>/<repo-name>.git

# Configure authentication
dvc remote modify origin --local auth basic
dvc remote modify origin --local user <your-username>
dvc remote modify origin --local password <your-dagshub-token>

# Get token from: Dagshub → Settings → Access Tokens → Generate Token
```

#### 3.3 Push Data to Dagshub

```powershell
# Push data to remote
dvc push

# Push DVC metadata to git (if connected to Dagshub git)
git push
```

### Step 4: Test Integration

```powershell
# Run training (will log to Dagshub)
python train.py --data data/processed/earthquakes_processed.parquet --experiment-name dagshub_test

# Generate and log profiling report
python etl/generate_profiling_report.py --input data/processed/earthquakes_processed.parquet --log-to-mlflow
```

**Verify:**
- Go to your Dagshub repository
- Check "Experiments" tab for MLflow runs
- Check "Data" tab for DVC-tracked files

### Step 5: Generate Profiling Report

```powershell
# Generate profiling report and save locally
python etl/generate_profiling_report.py --input data/processed/earthquakes_processed.parquet --output report.html

# Generate and log to MLflow (Dagshub)
python etl/generate_profiling_report.py --input data/processed/earthquakes_processed.parquet --log-to-mlflow
```

## Quick Reference Commands

### DVC Commands
```powershell
# Initialize
dvc init

# Add file to tracking
dvc add <file>

# Push to remote
dvc push

# Pull from remote
dvc pull

# Check status
dvc status
```

### MLflow Commands
```powershell
# View local MLflow UI
python -m mlflow ui

# List experiments
python -c "import mlflow; print(mlflow.list_experiments())"
```

## Troubleshooting

### DVC Issues
- **"DVC not found"**: `pip install dvc[s3]`
- **"Remote not configured"**: Run `dvc remote add origin <url>`
- **"Authentication failed"**: Check token in Dagshub settings

### MLflow Issues
- **"Connection refused"**: Check MLFLOW_TRACKING_URI format
- **"No experiments"**: Run training script first
- **"Can't log artifacts"**: Ensure Dagshub repo has MLflow enabled

## What Gets Tracked Where

| Item | Location | Tool |
|------|----------|------|
| Code | Git | GitHub/Dagshub |
| Data files | DVC Remote | Dagshub Storage |
| Data metadata | Git | GitHub/Dagshub |
| Models | MLflow | Dagshub MLflow |
| Experiments | MLflow | Dagshub MLflow |
| Profiling Reports | MLflow Artifacts | Dagshub MLflow |

## Next Phase: CI/CD (Phase III)

Once Dagshub is set up, you can proceed to:
1. Set up GitHub Actions
2. Create CI/CD workflows
3. Docker containerization
4. Model serving API

See `NEXT_STEPS.md` for Phase III details.

