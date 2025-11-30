# PowerShell script to reinitialize Airflow

Write-Host "Stopping all containers..." -ForegroundColor Yellow
docker-compose down

Write-Host "Removing old init container..." -ForegroundColor Yellow
docker rm airflow-init 2>$null

Write-Host "Reinitializing Airflow database..." -ForegroundColor Cyan
docker-compose up airflow-init

Write-Host "`nStarting all services..." -ForegroundColor Cyan
docker-compose up -d

Write-Host "`nWaiting 10 seconds for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "`nChecking container status..." -ForegroundColor Cyan
docker ps --format "table {{.Names}}\t{{.Status}}"

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "Access Airflow UI at: http://localhost:8080" -ForegroundColor Cyan
Write-Host "Username: airflow" -ForegroundColor Cyan
Write-Host "Password: airflow" -ForegroundColor Cyan

