# 🔍 Complete Dagshub Verification Guide - Step 6

Your repository: **https://dagshub.com/i222472/my-first-repo**

## 🎯 Overview

After your DAG completes, you should see:
- **Experiments**: Training runs with metrics
- **Artifacts**: Profiling reports and models
- **Data**: DVC-tracked files

---

## 📊 Step-by-Step Verification

### Part 1: Check Experiments Tab

1. **Go to**: https://dagshub.com/i222472/my-first-repo
2. **Click "Experiments" tab** (top navigation)
   - You should see a count like "Experiments (2)" or more

3. **What you'll see:**
   ```
   Experiments List:
   ├── earthquake_prediction_YYYYMMDD
   │   ├── Run 1: [Metrics: RMSE, MAE, R²]
   │   └── Run 2: [Metrics: RMSE, MAE, R²]
   └── data_profiling
       └── Run 1: [Profiling report artifact]
   ```

4. **Click on an experiment** (e.g., "earthquake_prediction_20241129")
   - See all runs in that experiment
   - Each run shows:
     - **Status**: Finished/Running
     - **Metrics**: RMSE, MAE, R² values
     - **Parameters**: Model type, hyperparameters
     - **Start Time**: When it ran

5. **Click on a specific run** to see:
   - **Overview**: Summary of the run
   - **Metrics**: Detailed metric values
   - **Parameters**: All hyperparameters used
   - **Artifacts**: Files logged (models, reports, etc.)

### Part 2: View MLflow UI (Detailed View)

1. **In the Experiments tab**, look for:
   - **"Open MLflow UI"** button (usually top right)
   - Or click on any experiment run

2. **MLflow UI Interface:**
   - **Left Sidebar**:
     - Experiments list
     - Filters (by metric, parameter, etc.)
   
   - **Main Panel**:
     - **Runs Table**: All runs with columns for metrics
     - **Compare Runs**: Select multiple runs to compare
     - **Charts**: Visualize metrics over time
   
   - **Run Details** (when you click a run):
     - **Overview Tab**: Basic info, metrics, parameters
     - **Artifacts Tab**: All files logged
     - **Metrics Tab**: Detailed metric history
     - **Parameters Tab**: All hyperparameters

3. **To find Profiling Report:**
   - Click on a run (especially from `generate_profiling_report` task)
   - Go to **"Artifacts"** tab
   - Look for `profiling_report/` folder
   - Click on the HTML file (e.g., `data_profile_report.html`)
   - It will open/download the profiling report

4. **To find Model Files:**
   - Click on a training run
   - Go to **"Artifacts"** tab
   - Look for `model/` folder
   - Contains:
     - `model.pkl` or similar (trained model)
     - `conda.yaml` (environment)
     - `requirements.txt` (dependencies)
     - Other model artifacts

### Part 3: Check Data Tab (DVC Files)

1. **Click "Data" tab** in your repository
2. **What you should see:**
   - DVC-tracked files
   - File structure similar to your local `data/` folder
   - Files like:
     - `data/processed/earthquakes_processed_YYYYMMDD.parquet`
     - `.dvc` metadata files

3. **Click on a file** to:
   - View file details
   - See version history
   - Download the file
   - See file size and metadata

4. **Verify DVC is working:**
   - Files should show version information
   - You should be able to see when files were added/modified

### Part 4: Check Model Registry

1. **Click "Models" tab**
2. **What you might see:**
   - Registered models (if you've registered any)
   - Model versions
   - Model stages (None/Staging/Production)

3. **If no models registered yet:**
   - That's OK - models are in MLflow experiments
   - You can register them later if needed

---

## ✅ Verification Checklist

After your DAG completed, check:

### Experiments Tab
- [ ] **Experiments visible**: At least 1-2 experiments listed
- [ ] **Runs visible**: Each experiment has runs
- [ ] **Metrics present**: RMSE, MAE, R² values shown
- [ ] **Status**: Runs show "Finished" status

### MLflow UI
- [ ] **Can access**: "Open MLflow UI" button works
- [ ] **Experiments list**: Shows all experiments
- [ ] **Run details**: Can click on runs and see details
- [ ] **Artifacts visible**: Can see artifacts section
- [ ] **Profiling report**: HTML file in artifacts
- [ ] **Model files**: Model artifacts present

### Data Tab
- [ ] **Files visible**: DVC-tracked files shown
- [ ] **File structure**: Matches your data directory
- [ ] **Version info**: Can see file versions/history

### Artifacts
- [ ] **Profiling report**: `profiling_report/data_profile_report.html` exists
- [ ] **Model files**: `model/` folder with model files
- [ ] **Can download**: Can download/view artifacts

---

## 🔍 Detailed Navigation

### Finding Your Training Runs

**Path 1: Via Experiments Tab**
1. Repository → **"Experiments"** tab
2. Click experiment: `earthquake_prediction_YYYYMMDD`
3. See all runs in that experiment
4. Click a run → See details

**Path 2: Via MLflow UI**
1. Click **"Open MLflow UI"**
2. Left sidebar → Select experiment
3. Main panel → See all runs
4. Click run → See details

### Finding Profiling Reports

**Method 1:**
1. Experiments tab → Find run with "profiling" in name
2. Click run → Artifacts tab
3. Open `profiling_report/` folder
4. Click HTML file

**Method 2:**
1. MLflow UI → Experiments
2. Look for experiment: `data_profiling`
3. Click run → Artifacts
4. Navigate to profiling report

### Understanding Metrics

**RMSE (Root Mean Squared Error)**:
- Lower is better
- Typical range: 0.3 - 0.8 for earthquake magnitude
- Shows average prediction error

**MAE (Mean Absolute Error)**:
- Lower is better
- Typical range: 0.2 - 0.6
- Shows average absolute error

**R² (R-squared)**:
- Higher is better (closer to 1.0)
- Range: 0.0 - 1.0
- Shows how well model fits data
- 0.7+ is good, 0.8+ is excellent

---

## 📸 What You Should See

### Experiments Tab Example:
```
Experiments (2)

┌─────────────────────────────────────────┐
│ earthquake_prediction_20241129          │
│ ├─ Run 1                                │
│ │  RMSE: 0.45  MAE: 0.32  R²: 0.78     │
│ │  Model: random_forest                 │
│ │  Status: Finished                     │
│ │  [View] [Compare]                     │
│ └─ Run 2                                │
│    RMSE: 0.42  MAE: 0.30  R²: 0.81     │
│    Model: gradient_boosting             │
│    Status: Finished                     │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ data_profiling                           │
│ └─ Run 1                                │
│    Artifacts: profiling_report/         │
│    Status: Finished                     │
└─────────────────────────────────────────┘
```

### Artifacts in a Run:
```
Artifacts/
├── profiling_report/
│   └── data_profile_report.html  [View] [Download]
├── model/
│   ├── model.pkl
│   ├── conda.yaml
│   └── requirements.txt
└── feature_importance.png (if generated)
```

---

## 🐛 Troubleshooting

### No Experiments Showing?

**Check:**
1. DAG completed successfully (all tasks green in Airflow)
2. MLflow enabled in Dagshub settings
3. Check Airflow logs:
   ```powershell
   docker-compose logs airflow-scheduler | Select-String "MLflow"
   docker-compose logs airflow-scheduler | Select-String "error"
   ```

**Fix:**
- Verify MLflow tracking URI is correct
- Check credentials in .env file
- Re-run the DAG

### Can't See Profiling Reports?

**Check:**
1. `generate_profiling_report` task completed
2. Check task logs in Airflow UI
3. Verify `--log-to-mlflow` flag was used

**Fix:**
- Check Airflow task logs for errors
- Manually test:
  ```powershell
  python etl/generate_profiling_report.py --input data/processed/earthquakes_processed.parquet --log-to-mlflow
  ```

### MLflow UI Not Loading?

**Possible causes:**
- MLflow not enabled in Dagshub settings
- Browser cache issues
- Network connectivity

**Fix:**
- Enable MLflow in repo settings
- Try incognito/private browsing
- Clear browser cache

### MLflow Version Warning?

I see Dagshub shows a warning about MLflow 3.x. I've updated `requirements.txt` to use MLflow < 3.0.0.

**If you see the warning:**
- It's just informational
- Your setup should still work
- To fix: Rebuild Docker image with updated requirements

---

## 🎯 Quick Verification Commands

### Check What Was Logged

```powershell
# Test MLflow connection
python -c "import mlflow; mlflow.set_tracking_uri('https://dagshub.com/i222472/my-first-repo.mlflow'); print('Connected!'); print(mlflow.list_experiments())"
```

### Check DVC Status

```powershell
# Check DVC remotes
python -m dvc remote list

# Check DVC status
python -m dvc status
```

---

## 🎉 Success Indicators

You'll know everything is working when:

✅ **Experiments tab** shows runs with metrics  
✅ **MLflow UI** accessible and shows detailed experiments  
✅ **Artifacts** contain profiling reports and models  
✅ **Data tab** shows DVC-tracked files  
✅ **Can download/view** all artifacts  
✅ **Metrics** are reasonable (RMSE < 1.0, R² > 0.5)

---

## 📝 Next Steps After Verification

Once you've verified everything:

1. **Document your findings**: Note which model performed best
2. **Review profiling reports**: Check data quality insights
3. **Move to Phase III**: CI/CD setup (when ready)

**Phase II is complete when all checkboxes above are checked!** ✅

