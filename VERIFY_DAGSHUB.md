# ✅ Complete Dagshub Verification Guide

Your repository: **https://dagshub.com/i222472/my-first-repo**

## 🎯 Step-by-Step Verification

### Step 1: Check Experiments Tab (MLflow Runs)

1. **Go to your repository**: https://dagshub.com/i222472/my-first-repo
2. **Click "Experiments" tab** (you should see a count, e.g., "Experiments (2)")
3. **What you should see:**
   - List of experiment runs
   - Each run shows:
     - Run name/ID
     - Status (Running/Finished)
     - Metrics (RMSE, MAE, R²)
     - Parameters (model type, hyperparameters)
     - Start time

4. **Click on a run** to see details:
   - **Metrics**: RMSE, MAE, R², etc.
   - **Parameters**: Model type, n_estimators, etc.
     - **Artifacts**: 
       - Profiling report (HTML file)
       - Trained model files
       - Feature importance plots (if generated)

### Step 2: Open MLflow UI (Detailed View)

1. **In the Experiments tab**, look for:
   - **"Open MLflow UI"** button (usually at the top right)
   - Or click on a specific experiment run

2. **MLflow UI shows:**
   - **Experiments list**: All your experiments
   - **Runs**: Individual training runs
   - **Compare runs**: Side-by-side comparison
   - **Metrics**: Charts showing metric values
   - **Parameters**: All hyperparameters
   - **Artifacts**: 
     - `profiling_report/` folder → Contains HTML profiling report
     - `model/` folder → Contains trained model files
     - Any other artifacts logged

3. **To view profiling report:**
   - Click on a run
   - Go to "Artifacts" section
   - Click on `profiling_report/` folder
   - Click on the HTML file to view/download

### Step 3: Check Data Tab (DVC Files)

1. **Click "Data" tab** in your repository
2. **What you should see:**
   - DVC-tracked files
   - File versions/history
   - File sizes
   - Last modified dates

3. **Look for:**
   - `data/processed/earthquakes_processed_*.parquet` files
   - `.dvc` metadata files
   - Any other data files you've versioned

4. **Click on a file** to:
   - View file details
   - See version history
   - Download the file

### Step 4: Check Model Registry

1. **Click "Models" tab**
2. **What you should see:**
   - Registered models (if any)
   - Model versions
   - Model metadata

3. **If models are registered:**
   - Model name
   - Version number
   - Stage (None/Staging/Production)
   - Metrics
   - Artifacts

### Step 5: Verify Profiling Reports

1. **Go to Experiments tab**
2. **Click on a run** (especially the `generate_profiling_report` run)
3. **Click "Artifacts"** section
4. **Look for:**
   - `profiling_report/` folder
   - Inside: `data_profile_report.html` or similar
5. **Click the HTML file** to:
   - View the report in browser
   - Download it

### Step 6: Verify Training Metrics

1. **In Experiments tab**, click on a training run
2. **Check metrics section:**
   - **RMSE** (Root Mean Squared Error) - lower is better
   - **MAE** (Mean Absolute Error) - lower is better
   - **R²** (R-squared) - higher is better (closer to 1.0)
3. **Compare multiple runs** to see which model performed best

## 📊 What to Look For

### ✅ Success Indicators:

**Experiments Tab:**
- [ ] At least 2 experiment runs visible
- [ ] Each run shows metrics (RMSE, MAE, R²)
- [ ] Runs have status "Finished" or "Running"
- [ ] Artifacts section has files

**MLflow UI:**
- [ ] Can see experiment list
- [ ] Can compare runs
- [ ] Metrics charts are visible
- [ ] Artifacts are downloadable

**Data Tab:**
- [ ] DVC-tracked files are visible
- [ ] File versions are tracked
- [ ] Can see file history

**Artifacts:**
- [ ] Profiling report HTML file exists
- [ ] Model files are present
- [ ] Can download/view artifacts

## 🔍 Detailed Navigation Guide

### Finding Your Experiments

1. **Repository Home** → Click **"Experiments"** tab
2. **Experiments List** → Shows all experiments
   - Experiment name (e.g., "earthquake_prediction_20241129")
   - Number of runs
   - Last run time

3. **Click on an experiment** → See all runs in that experiment
4. **Click on a run** → See detailed information

### Understanding the MLflow UI

**Left Sidebar:**
- **Experiments**: List of all experiments
- **Runs**: All runs across experiments
- **Models**: Model registry

**Main Panel:**
- **Runs Table**: Shows all runs with metrics
- **Compare**: Select runs to compare side-by-side
- **Charts**: Visualize metrics over time

**Run Details:**
- **Overview**: Basic info, metrics, parameters
- **Artifacts**: Files logged with the run
- **Metrics**: Detailed metric values
- **Parameters**: All hyperparameters used

### Finding Profiling Reports

**Method 1: Via Experiments Tab**
1. Click "Experiments" tab
2. Find run with name containing "profiling" or check the `generate_profiling_report` task
3. Click on the run
4. Go to "Artifacts" section
5. Look for `profiling_report/` folder
6. Click HTML file to view

**Method 2: Via MLflow UI**
1. Click "Open MLflow UI"
2. Select experiment
3. Click on a run
4. Scroll to "Artifacts"
5. Navigate to profiling report

## 🎯 Quick Verification Checklist

After your DAG completed, verify:

- [ ] **Experiments tab** shows runs (count > 0)
- [ ] **At least one training run** with metrics (RMSE, MAE, R²)
- [ ] **Profiling report** visible in artifacts
- [ ] **Model files** present in artifacts
- [ ] **Data tab** shows DVC-tracked files
- [ ] **MLflow UI** accessible and working
- [ ] **Can download/view** artifacts

## 📸 What You Should See

### Experiments Tab:
```
Experiments (2)
├── earthquake_prediction_20241129
│   ├── Run 1: RMSE=0.45, MAE=0.32, R²=0.78
│   └── Run 2: RMSE=0.42, MAE=0.30, R²=0.81
└── data_profiling
    └── Run 1: Profiling report artifact
```

### Artifacts in a Run:
```
Artifacts/
├── profiling_report/
│   └── data_profile_report.html
├── model/
│   ├── model.pkl
│   └── conda.yaml
└── feature_importance.png (if generated)
```

## 🐛 Troubleshooting

### No Experiments Showing?

**Check:**
1. DAG completed successfully (all tasks green)
2. MLflow is enabled in Dagshub settings
3. Tracking URI is correct in docker-compose.yml
4. Check Airflow logs for MLflow errors

**Fix:**
```powershell
# Check if MLflow tracking is working
docker-compose logs airflow-scheduler | Select-String "MLflow"
docker-compose logs airflow-scheduler | Select-String "error"
```

### Can't See Profiling Reports?

**Check:**
1. `generate_profiling_report` task completed successfully
2. Check task logs in Airflow UI
3. Verify `--log-to-mlflow` flag was used

**Fix:**
- Re-run the DAG
- Or manually generate report:
```powershell
python etl/generate_profiling_report.py --input data/processed/earthquakes_processed.parquet --log-to-mlflow
```

### MLflow UI Not Loading?

**Check:**
1. MLflow is enabled in Dagshub settings
2. You're logged into Dagshub
3. Repository permissions are correct

**Fix:**
- Refresh the page
- Try incognito/private browsing
- Check Dagshub status page

## 🎉 Success!

If you can see:
- ✅ Experiments with metrics
- ✅ Profiling reports in artifacts
- ✅ Model files
- ✅ DVC-tracked data

**Then Phase II is 100% complete!** 🎊

## 📝 Next: Phase III

Once verified, you can move to:
- Phase III: CI/CD setup
- Phase IV: Monitoring with Prometheus/Grafana

