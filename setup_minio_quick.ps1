# Quick MinIO Setup Script for Windows

Write-Host "Setting up MinIO for DVC storage..." -ForegroundColor Green

# Check if Docker is available
try {
    $dockerVersion = docker --version
    Write-Host "Docker found: $dockerVersion" -ForegroundColor Cyan
    $useDocker = $true
} catch {
    Write-Host "Docker not found. Will use MinIO binary instead." -ForegroundColor Yellow
    $useDocker = $false
}

# Step 1: Start MinIO
if ($useDocker) {
    Write-Host "`nStarting MinIO with Docker..." -ForegroundColor Yellow
    
    # Check if MinIO container already exists
    $existing = docker ps -a --filter "name=minio" --format "{{.Names}}"
    if ($existing -eq "minio") {
        Write-Host "MinIO container exists. Starting it..." -ForegroundColor Cyan
        docker start minio
    } else {
        Write-Host "Creating new MinIO container..." -ForegroundColor Cyan
        docker run -d `
            -p 9000:9000 `
            -p 9001:9001 `
            --name minio `
            -v ${PWD}\minio-data:/data `
            -e "MINIO_ROOT_USER=minioadmin" `
            -e "MINIO_ROOT_PASSWORD=minioadmin" `
            minio/minio server /data --console-address ":9001"
    }
    
    Write-Host "✓ MinIO started!" -ForegroundColor Green
    Write-Host "  Console: http://localhost:9001" -ForegroundColor Cyan
    Write-Host "  API: http://localhost:9000" -ForegroundColor Cyan
    Write-Host "  Login: minioadmin / minioadmin" -ForegroundColor Cyan
} else {
    Write-Host "`nPlease download and run MinIO manually:" -ForegroundColor Yellow
    Write-Host "  1. Download from: https://min.io/download" -ForegroundColor Cyan
    Write-Host "  2. Run: .\minio.exe server D:\minio-data --console-address `":9001`"" -ForegroundColor Cyan
}

# Step 2: Configure DVC
Write-Host "`nConfiguring DVC with MinIO..." -ForegroundColor Yellow

# Check if DVC is installed
try {
    python -m dvc --version | Out-Null
} catch {
    Write-Host "ERROR: DVC not found. Install with: pip install dvc[s3]" -ForegroundColor Red
    exit 1
}

# Remove existing remote if it exists
$existingRemote = python -m dvc remote list 2>&1
if ($existingRemote -match "minio-storage") {
    Write-Host "Removing existing minio-storage remote..." -ForegroundColor Cyan
    python -m dvc remote remove minio-storage
}

# Add MinIO remote
Write-Host "Adding MinIO remote..." -ForegroundColor Cyan
python -m dvc remote add -d minio-storage s3://earthquake-data
python -m dvc remote modify minio-storage endpointurl http://localhost:9000
python -m dvc remote modify minio-storage access_key_id minioadmin
python -m dvc remote modify minio-storage secret_access_key minioadmin

Write-Host "✓ DVC configured with MinIO!" -ForegroundColor Green

# Step 3: Instructions
Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Open MinIO Console: http://localhost:9001" -ForegroundColor White
Write-Host "2. Login with: minioadmin / minioadmin" -ForegroundColor White
Write-Host "3. Create bucket named: earthquake-data" -ForegroundColor White
Write-Host "4. Push your data: python -m dvc push" -ForegroundColor White
Write-Host "="*60 -ForegroundColor Cyan

Write-Host "`n✓ Setup complete!" -ForegroundColor Green

