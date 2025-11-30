# ⚡ Quick Start: Docker Setup (Windows-Friendly)

## 🎯 3-Step Setup

### Step 1: Create .env File

```powershell
echo "AIRFLOW_UID=50000" > .env
```

### Step 2: Create Directories

```powershell
mkdir -p logs plugins
```

### Step 3: Start Everything

```powershell
# Initialize Airflow (first time only)
docker-compose up airflow-init

# Start all services
docker-compose up -d
```

## ✅ Access Services

- **Airflow UI**: http://localhost:8080 (airflow/airflow)
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

## 🚀 Run Your DAG

1. Open http://localhost:8080
2. Find `earthquake_etl_pipeline`
3. Toggle ON → Trigger DAG

## 📚 Full Guide

See **[DOCKER_SETUP_GUIDE.md](DOCKER_SETUP_GUIDE.md)** for detailed instructions and troubleshooting.

