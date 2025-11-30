# Dagshub Setup Script for Windows PowerShell
# This script configures DVC and MLflow to work with Dagshub

param(
    [Parameter(Mandatory=$true)]
    [string]$DagshubToken
)

Write-Host "Setting up Dagshub integration..." -ForegroundColor Green
Write-Host ""

# Step 1: Configure DVC Remote
Write-Host "Step 1: Configuring DVC remote to Dagshub..." -ForegroundColor Cyan

# Remove existing dagshub remote if it exists
$existingRemote = python -m dvc remote list 2>&1
if ($existingRemote -match "dagshub") {
    Write-Host "Removing existing dagshub remote..." -ForegroundColor Yellow
    python -m dvc remote remove dagshub 2>$null
}

# Add Dagshub remote
Write-Host "Adding Dagshub as DVC remote..." -ForegroundColor Yellow
python -m dvc remote add dagshub https://dagshub.com/i222472/my-first-repo.git

# Configure authentication
Write-Host "Configuring DVC authentication..." -ForegroundColor Yellow
python -m dvc remote modify dagshub --local auth basic
python -m dvc remote modify dagshub --local user i222472
python -m dvc remote modify dagshub --local password $DagshubToken

Write-Host "[OK] DVC remote configured!" -ForegroundColor Green
Write-Host ""

# Step 2: Create .env file for MLflow
Write-Host "Step 2: Creating .env file for MLflow credentials..." -ForegroundColor Cyan

$envContent = "MLFLOW_TRACKING_URI=https://dagshub.com/i222472/my-first-repo.mlflow`nMLFLOW_TRACKING_USERNAME=i222472`nMLFLOW_TRACKING_PASSWORD=$DagshubToken"

$envContent | Out-File -FilePath .env -Encoding utf8 -NoNewline

Write-Host "[OK] .env file created!" -ForegroundColor Green
Write-Host ""

# Step 3: Verify configuration
Write-Host "Step 3: Verifying configuration..." -ForegroundColor Cyan

Write-Host "DVC Remotes:" -ForegroundColor Yellow
python -m dvc remote list

Write-Host ""
Write-Host "[OK] Setup complete!" -ForegroundColor Green
Write-Host ""

# Step 4: Instructions
$separator = "=" * 60
Write-Host $separator -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Make sure MLflow and DVC are enabled in Dagshub repo settings" -ForegroundColor White
Write-Host "2. Set token for Docker: `$env:DAGSHUB_TOKEN = '$DagshubToken'" -ForegroundColor White
Write-Host "3. Restart Docker containers: docker-compose down" -ForegroundColor White
Write-Host "   Then: docker-compose up -d" -ForegroundColor White
Write-Host "4. Run your DAG in Airflow" -ForegroundColor White
Write-Host "5. Check Dagshub: https://dagshub.com/i222472/my-first-repo" -ForegroundColor White
Write-Host "   - Go to 'Experiments' tab to see MLflow runs" -ForegroundColor White
Write-Host "   - Go to 'Data' tab to see DVC-tracked files" -ForegroundColor White
Write-Host $separator -ForegroundColor Cyan
Write-Host ""

Write-Host "[WARNING] IMPORTANT: Add .env to .gitignore to keep your token secure!" -ForegroundColor Red
Write-Host "   Run: Add-Content .gitignore '.env'" -ForegroundColor Yellow
