# 🔧 Fix Airflow Initialization Issue

## Problem
The airflow-scheduler is restarting because the database wasn't initialized properly.

## Solution

Run these commands in your PowerShell terminal:

```powershell
# Make sure you're in the project directory
cd "D:\semester 7\mlops\Project\secondtry\MLOPS_FINAL_PROJECT_NewsData_API"

# Stop all containers
docker-compose down

# Remove the old init container (if exists)
docker rm airflow-init 2>$null

# Re-run initialization
docker-compose up airflow-init

# Wait for it to complete, then start everything
docker-compose up -d
```

## Alternative: Manual Database Init

If the above doesn't work, manually initialize:

```powershell
# Stop containers
docker-compose down

# Start only PostgreSQL
docker-compose up -d postgres

# Wait 10 seconds for PostgreSQL to be ready
Start-Sleep -Seconds 10

# Run init manually
docker-compose run --rm airflow-scheduler airflow db init
docker-compose run --rm airflow-scheduler airflow users create --username airflow --firstname Admin --lastname User --role Admin --email admin@example.com --password airflow

# Now start everything
docker-compose up -d
```

## Verify It Worked

```powershell
# Check containers
docker ps

# Should show:
# - postgres: Up (healthy)
# - minio: Up
# - airflow-webserver: Up
# - airflow-scheduler: Up (not restarting!)

# Check scheduler logs (should not show database errors)
docker logs airflow-scheduler --tail 20
```

## Access Airflow

Once scheduler is running:
- **URL**: http://localhost:8080
- **Username**: `airflow`
- **Password**: `airflow`

