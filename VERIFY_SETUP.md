# ✅ Setup Verification - Next Steps

## 🎉 Success! All Services Started

Your Docker containers are running:
- ✅ **PostgreSQL** - Database for Airflow
- ✅ **MinIO** - Object storage
- ✅ **Airflow Init** - Completed (exited normally)
- ✅ **Airflow Webserver** - Running
- ✅ **Airflow Scheduler** - Running

## 🌐 Access Your Services

### 1. Airflow UI

**URL:** http://localhost:8080

**Login:**
- Username: `airflow`
- Password: `airflow`

**What to do:**
1. Open the URL in your browser
2. Login with credentials above
3. Look for DAG: `earthquake_etl_pipeline`
4. Toggle it ON (switch on the left)
5. Click ▶️ → "Trigger DAG"
6. Watch it run!

### 2. MinIO Console

**URL:** http://localhost:9001

**Login:**
- Username: `minioadmin`
- Password: `minioadmin`

**What to do:**
1. Open the URL
2. Login
3. Create bucket: `earthquake-data` (if not exists)
4. You'll see uploaded files here after DAG runs

## 🚀 Run Your First DAG

### Step-by-Step:

1. **Open Airflow UI**: http://localhost:8080
2. **Find your DAG**: `earthquake_etl_pipeline`
3. **Enable it**: Click the toggle switch (left side)
4. **Trigger it**: Click the ▶️ play button → "Trigger DAG"
5. **Monitor**: Click on the DAG name to see the graph view
6. **Watch tasks**: They'll turn green (✅) when complete

### Expected Pipeline Flow:

```
extract_data → quality_check → transform_data → 
upload_to_minio → version_data → generate_profiling_report → train_model
```

## 🔍 Check Logs

If something fails, check logs:

```powershell
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs airflow-scheduler
docker-compose logs airflow-webserver
docker-compose logs minio

# Follow logs in real-time
docker-compose logs -f airflow-scheduler
```

## ✅ Verify Everything Works

### Quick Test:

```powershell
# Check all containers are running
docker-compose ps

# Should show:
# - postgres: Up
# - minio: Up  
# - airflow-webserver: Up
# - airflow-scheduler: Up
```

### Test MinIO Connection:

```powershell
# Access Airflow container
docker-compose exec airflow-scheduler bash

# Test MinIO (inside container)
curl http://minio:9000/minio/health/live

# Exit container
exit
```

## 🐛 Troubleshooting

### DAG Not Appearing?

```powershell
# Check DAGs folder is mounted
docker-compose exec airflow-scheduler ls -la /opt/airflow/dags

# Check for syntax errors
docker-compose logs airflow-scheduler | Select-String "error"
```

### Can't Access Airflow UI?

```powershell
# Check webserver is running
docker-compose ps airflow-webserver

# Check logs
docker-compose logs airflow-webserver

# Restart if needed
docker-compose restart airflow-webserver
```

### Tasks Failing?

1. **Check task logs in Airflow UI:**
   - Click on failed task
   - Click "Log" tab
   - Read error message

2. **Common issues:**
   - MinIO not accessible: Check `MINIO_ENDPOINT` is `http://minio:9000` in Docker
   - DVC not configured: DVC config should be in `.dvc` folder
   - Missing dependencies: Check `requirements.txt` is mounted

## 📊 Monitor Progress

### In Airflow UI:

- **Graph View**: See task dependencies
- **Tree View**: See historical runs
- **Gantt View**: See timing
- **Logs**: Detailed output for each task

### Check Outputs:

**After DAG completes:**

1. **MinIO Console**: http://localhost:9001
   - Check `earthquake-data` bucket
   - Should see uploaded files

2. **Local Files** (if mounted):
   - `data/raw/earthquakes_combined.geojson`
   - `data/processed/earthquakes_processed_*.parquet`

3. **MLflow** (if configured):
   - Run `mlflow ui` locally
   - Or check Dagshub if configured

## 🎯 Next Steps

After successful DAG run:

1. ✅ **Verify outputs** in MinIO Console
2. ✅ **Check MLflow** for model and profiling report
3. ✅ **Set up Dagshub** for remote MLflow tracking
4. ✅ **Configure CI/CD** with GitHub Actions

## 📚 Useful Commands

```powershell
# Stop all services
docker-compose down

# Start services
docker-compose up -d

# Restart a service
docker-compose restart airflow-scheduler

# View logs
docker-compose logs -f

# Access container shell
docker-compose exec airflow-scheduler bash

# Rebuild after code changes
docker-compose build
docker-compose up -d
```

## 🎉 You're Ready!

Everything is set up and running. Go to http://localhost:8080 and trigger your DAG!

