# 🔧 Manual Airflow Initialization

Since the automatic init is having issues, here's how to manually initialize:

## Step 1: Start Only PostgreSQL

```powershell
docker-compose up -d postgres
```

Wait 10 seconds for PostgreSQL to be ready.

## Step 2: Manually Initialize Database

```powershell
# Run db init in a temporary container
docker-compose run --rm airflow-scheduler airflow db init

# Create admin user
docker-compose run --rm airflow-scheduler airflow users create \
  --username airflow \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password airflow
```

## Step 3: Start All Services

```powershell
docker-compose up -d
```

## Verify

```powershell
# Check scheduler is running
docker ps | Select-String "airflow-scheduler"
# Should show "Up" not "Restarting"
```

## Access Airflow

- **URL**: http://localhost:8080
- **Username**: `airflow`
- **Password**: `airflow`

