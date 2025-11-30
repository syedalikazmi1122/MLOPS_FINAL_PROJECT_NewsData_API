# 🔧 Quick Fix for Airflow Init

## The Problem
The airflow-init container can't find the `airflow` command because of PATH issues.

## Solution

Run these commands:

```powershell
# 1. Stop everything
docker-compose down

# 2. Rebuild the Airflow image (with fixes)
docker-compose build

# 3. Re-initialize
docker-compose up airflow-init

# 4. Start all services
docker-compose up -d
```

## Or Use the Script

I've created a PowerShell script that does everything:

```powershell
.\REINIT_AIRFLOW.ps1
```

## Verify It Worked

```powershell
# Check scheduler is running (not restarting)
docker ps | Select-String "airflow-scheduler"

# Should show "Up" not "Restarting"
```

## Then Access Airflow

- **URL**: http://localhost:8080
- **Username**: `airflow`
- **Password**: `airflow`

