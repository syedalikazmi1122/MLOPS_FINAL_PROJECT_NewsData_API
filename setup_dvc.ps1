# DVC Setup Script for Windows PowerShell

Write-Host "Setting up DVC for data versioning..." -ForegroundColor Green

# Check if DVC is installed
try {
    $dvcVersion = dvc --version
    Write-Host "DVC version: $dvcVersion" -ForegroundColor Cyan
} catch {
    Write-Host "ERROR: DVC not found. Install with: pip install dvc[s3]" -ForegroundColor Red
    exit 1
}

# Initialize DVC (if not already initialized)
if (-not (Test-Path ".dvc")) {
    Write-Host "Initializing DVC..." -ForegroundColor Yellow
    dvc init
    Write-Host "✓ DVC initialized" -ForegroundColor Green
} else {
    Write-Host "DVC already initialized" -ForegroundColor Cyan
}

# Add processed data to DVC
if (Test-Path "data/processed/earthquakes_processed.parquet") {
    Write-Host "Adding processed data to DVC..." -ForegroundColor Yellow
    dvc add data/processed/earthquakes_processed.parquet
    Write-Host "✓ Data added to DVC" -ForegroundColor Green
} else {
    Write-Host "WARNING: Processed data file not found!" -ForegroundColor Red
    Write-Host "Run: python etl/transform_data.py --input data/raw/earthquakes_combined.geojson --output data/processed/earthquakes_processed.parquet" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✓ DVC setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Review the generated .dvc and .gitignore files"
Write-Host "2. Commit DVC metadata to git:"
Write-Host "   git add data/processed/earthquakes_processed.parquet.dvc .gitignore"
Write-Host "   git commit -m 'Add processed data to DVC'"
Write-Host ""
Write-Host "3. To configure remote storage (Dagshub), see NEXT_STEPS.md"

