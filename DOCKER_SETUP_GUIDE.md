# 🐳 Complete Docker Setup Guide for Airflow + MinIO

This guide shows you how to run **everything via Docker** - perfect for Windows users!

## ✅ Why Docker?

- ✅ **No Windows compatibility issues** (Airflow runs in Linux container)
- ✅ **Easy setup** - everything configured in one file
- ✅ **Isolated environment** - won't conflict with your system
- ✅ **Production-ready** - same setup works everywhere

## 📋 What's Included

The `docker-compose.yml` sets up:

1. **MinIO** - Object storage (ports 9000, 9001)
2. **PostgreSQL** - Airflow database
3. **Airflow Scheduler** - Runs your DAGs
4. **Airflow Webserver** - Web UI (port 8080)
5. **Airflow Init** - One-time database initialization

## 🚀 Quick Start (5 Steps)

### Step 1: Create .env File

Create `.env` file in project root:

```powershell
# For Windows, set AIRFLOW_UID to 50000 (default)
echo "AIRFLOW_UID=50000" > .env
```

Or manually create `.env` with:
```
AIRFLOW_UID=50000
```

### Step 2: Create Required Directories

```powershell
# Create directories for Airflow
mkdir -p logs plugins
```

### Step 3: Initialize Airflow Database

```powershell
# This will build the Airflow image and initialize the database
docker-compose up airflow-init
```

**Expected output:**
```
✅ Database initialized
✅ Admin user created (username: airflow, password: airflow)
```

### Step 4: Start All Services

```powershell
# Start everything in background
docker-compose up -d
```

**This starts:**
- MinIO (ports 9000, 9001)
- PostgreSQL (internal)
- Airflow Scheduler
- Airflow Webserver (port 8080)

### Step 5: Access the Services

**Airflow UI:**
- URL: http://localhost:8080
- Username: `airflow`
- Password: `airflow`

**MinIO Console:**
- URL: http://localhost:9001
- Username: `minioadmin`
- Password: `minioadmin`

## 🎯 Run Your DAG

1. **Open Airflow UI**: http://localhost:8080
2. **Find DAG**: Look for `earthquake_etl_pipeline`
3. **Toggle ON**: Click the toggle switch
4. **Trigger**: Click ▶️ → "Trigger DAG"
5. **Monitor**: Watch tasks execute in real-time!

## 📁 Directory Structure

Your project structure should look like:

```
project-root/
├── dags/
│   └── earthquake_etl_dag.py
├── data/
│   ├── raw/
│   └── processed/
├── etl/
│   ├── download_historical.py
│   ├── data_quality_check.py
│   ├── transform_data.py
│   ├── upload_to_minio.py
│   └── generate_profiling_report.py
├── train.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile.airflow
├── .env
├── logs/          # Created by Airflow
└── plugins/       # Created by Airflow
```

## 🔧 Configuration

### Environment Variables

You can customize settings in `docker-compose.yml` or create `.env`:

```env
# Airflow
AIRFLOW_UID=50000
AIRFLOW__CORE__LOAD_EXAMPLES=false
AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=true

# MinIO (already configured)
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=earthquake-data

# MLflow (optional - for Dagshub)
# MLFLOW_TRACKING_URI=https://dagshub.com/username/repo.mlflow
```

### MinIO Connection from Airflow

The DAG automatically uses:
- Endpoint: `http://minio:9000` (internal Docker network)
- Credentials: `minioadmin` / `minioadmin`

**Note:** From inside the Airflow container, use `minio:9000` (not `localhost:9000`)

## 🛠️ Common Commands

### Start Services
```powershell
docker-compose up -d
```

### Stop Services
```powershell
docker-compose down
```

### View Logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f airflow-scheduler
docker-compose logs -f airflow-webserver
docker-compose logs -f minio
```

### Restart a Service
```powershell
docker-compose restart airflow-scheduler
```

### Rebuild After Code Changes
```powershell
# Rebuild Airflow image (if you changed Dockerfile or requirements.txt)
docker-compose build airflow-scheduler airflow-webserver

# Restart services
docker-compose up -d
```

### Access Container Shell
```powershell
# Access Airflow container
docker-compose exec airflow-scheduler bash

# Inside container, you can run:
python -m dvc --version
python train.py --help
```

### Check Service Status
```powershell
docker-compose ps
```

## 🐛 Troubleshooting

### Services Won't Start

**Check Docker is running:**
```powershell
docker ps
```

**Check for port conflicts:**
```powershell
# Check if ports are in use
netstat -ano | findstr :8080
netstat -ano | findstr :9000
netstat -ano | findstr :9001
```

**View error logs:**
```powershell
docker-compose logs
```

### DAG Not Appearing

**Check DAGs folder is mounted:**
```powershell
# Verify dags folder exists
Test-Path dags

# Check DAG file syntax
docker-compose exec airflow-scheduler python -m py_compile /opt/airflow/dags/earthquake_etl_dag.py
```

**Check Airflow logs:**
```powershell
docker-compose logs airflow-scheduler | Select-String "error"
```

### MinIO Connection Issues

**From Airflow container, MinIO is at `http://minio:9000`** (not localhost)

The DAG is already configured correctly. If you need to test:

```powershell
# Access Airflow container
docker-compose exec airflow-scheduler bash

# Test MinIO connection
curl http://minio:9000/minio/health/live
```

### Database Issues

**Reset Airflow database:**
```powershell
# Stop services
docker-compose down

# Remove database volume
docker volume rm mlops_final_project_newsdata_api_postgres-db-volume

# Re-initialize
docker-compose up airflow-init
docker-compose up -d
```

### Permission Issues

**On Windows, set AIRFLOW_UID:**
```powershell
# In .env file
AIRFLOW_UID=50000
```

## 📊 Verify Everything Works

### 1. Check Services are Running
```powershell
docker-compose ps
```

All services should show "Up" status.

### 2. Access Airflow UI
- Open http://localhost:8080
- Login: `airflow` / `airflow`
- You should see `earthquake_etl_pipeline` DAG

### 3. Access MinIO Console
- Open http://localhost:9001
- Login: `minioadmin` / `minioadmin`
- Create bucket: `earthquake-data`

### 4. Test DAG
- In Airflow UI, toggle DAG ON
- Click ▶️ → "Trigger DAG"
- Watch tasks execute

## 🔄 Update Code

When you update your code:

1. **Code changes are automatically reflected** (volumes are mounted)
2. **For requirements.txt changes**, rebuild:
   ```powershell
   docker-compose build
   docker-compose up -d
   ```

## 📝 Next Steps

After Docker setup:

1. ✅ **Test the DAG** - Trigger it from Airflow UI
2. ✅ **Set up Dagshub** - Configure MLflow tracking
3. ✅ **Configure CI/CD** - GitHub Actions workflows
4. ✅ **Add Monitoring** - Prometheus & Grafana

## 🎓 Additional Resources

- [Airflow Docker Documentation](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html)
- [MinIO Docker Guide](https://docs.min.io/docs/minio-docker-quickstart-guide.html)
- [Docker Compose Reference](https://docs.docker.com/compose/)

## ✅ Success Checklist

- [ ] Docker Desktop is running
- [ ] `.env` file created with `AIRFLOW_UID=50000`
- [ ] `docker-compose up airflow-init` completed successfully
- [ ] `docker-compose up -d` started all services
- [ ] Airflow UI accessible at http://localhost:8080
- [ ] MinIO Console accessible at http://localhost:9001
- [ ] DAG `earthquake_etl_pipeline` visible in Airflow UI
- [ ] Can trigger and run DAG successfully

