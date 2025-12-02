# Complete MLOps Pipeline Test Script
Write-Host "🚀 Starting Complete MLOps Pipeline Test..." -ForegroundColor Green
Write-Host "=" * 60
Write-Host ""

# Step 1: Check Services
Write-Host "1️⃣  Checking Services..." -ForegroundColor Cyan
$services = @("minio", "postgres", "airflow-webserver", "api", "prometheus", "grafana")
$allRunning = $true
foreach ($service in $services) {
    $running = docker ps --filter "name=$service" --format "{{.Names}}"
    if ($running) {
        Write-Host "   ✅ $service is running" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $service is NOT running" -ForegroundColor Red
        $allRunning = $false
    }
}

if (-not $allRunning) {
    Write-Host "`n⚠️  Some services are not running. Start them with: docker-compose up -d" -ForegroundColor Yellow
}

# Step 2: Test API
Write-Host "`n2️⃣  Testing API..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -ErrorAction Stop
    Write-Host "   ✅ API Health: $($health.status)" -ForegroundColor Green
    Write-Host "   📊 Model Loaded: $($health.model_loaded)" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ API not accessible at http://localhost:8000" -ForegroundColor Red
    Write-Host "   💡 Start API with: docker-compose up -d api" -ForegroundColor Yellow
}

# Step 3: Test Metrics Endpoint
Write-Host "`n3️⃣  Testing Metrics Endpoint..." -ForegroundColor Cyan
try {
    $metrics = Invoke-WebRequest -Uri "http://localhost:8000/metrics" -ErrorAction Stop
    $requestCount = ($metrics.Content -split "`n" | Select-String "api_requests_total").Count
    Write-Host "   ✅ Metrics endpoint working" -ForegroundColor Green
    Write-Host "   📊 Found $requestCount metric entries" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Metrics endpoint not accessible" -ForegroundColor Red
}

# Step 4: Generate Metrics
Write-Host "`n4️⃣  Generating Metrics (20 requests)..." -ForegroundColor Cyan
$successCount = 0
for ($i=1; $i -le 20; $i++) {
    try {
        Invoke-RestMethod -Uri "http://localhost:8000/health" -ErrorAction Stop | Out-Null
        $successCount++
        if ($i % 5 -eq 0) {
            Write-Host "   ✓ $i requests completed..." -ForegroundColor Gray
        }
    } catch {
        Write-Host "   ✗ Request $i failed" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 500
}
Write-Host "   ✅ Generated $successCount successful requests" -ForegroundColor Green

# Step 5: Check Prometheus
Write-Host "`n5️⃣  Checking Prometheus..." -ForegroundColor Cyan
try {
    $query = "api_requests_total"
    $url = "http://localhost:9090/api/v1/query?query=$query"
    $response = Invoke-RestMethod -Uri $url -ErrorAction Stop
    if ($response.data.result.Count -gt 0) {
        Write-Host "   ✅ Prometheus has metrics" -ForegroundColor Green
        Write-Host "   📊 Found $($response.data.result.Count) metric series" -ForegroundColor Cyan
        
        # Show sample data
        if ($response.data.result.Count -gt 0) {
            $sample = $response.data.result[0]
            Write-Host "   📈 Sample: $($sample.metric.endpoint) - $($sample.metric.status)" -ForegroundColor Gray
        }
    } else {
        Write-Host "   ⚠️  Prometheus running but no metrics yet (wait 10-15 seconds)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Prometheus not accessible at http://localhost:9090" -ForegroundColor Red
    Write-Host "   💡 Start Prometheus with: docker-compose up -d prometheus" -ForegroundColor Yellow
}

# Step 6: Check Prometheus Targets
Write-Host "`n6️⃣  Checking Prometheus Targets..." -ForegroundColor Cyan
try {
    $targetsUrl = "http://localhost:9090/api/v1/targets"
    $targets = Invoke-RestMethod -Uri $targetsUrl -ErrorAction Stop
    $activeTargets = $targets.data.activeTargets | Where-Object { $_.health -eq "up" }
    Write-Host "   ✅ Found $($activeTargets.Count) active targets" -ForegroundColor Green
    foreach ($target in $activeTargets) {
        Write-Host "   📍 $($target.labels.job): $($target.health)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ⚠️  Could not check targets" -ForegroundColor Yellow
}

# Step 7: Check Grafana
Write-Host "`n7️⃣  Checking Grafana..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Grafana is accessible" -ForegroundColor Green
        Write-Host "   🌐 Dashboard: http://localhost:3000" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ❌ Grafana not accessible at http://localhost:3000" -ForegroundColor Red
    Write-Host "   💡 Start Grafana with: docker-compose up -d grafana" -ForegroundColor Yellow
}

# Step 8: Check MinIO
Write-Host "`n8️⃣  Checking MinIO..." -ForegroundColor Cyan
try {
    $minioHealth = Invoke-WebRequest -Uri "http://localhost:9000/minio/health/live" -ErrorAction Stop
    if ($minioHealth.StatusCode -eq 200) {
        Write-Host "   ✅ MinIO is accessible" -ForegroundColor Green
        Write-Host "   🌐 Console: http://localhost:9001 (minioadmin/minioadmin)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ❌ MinIO not accessible" -ForegroundColor Red
}

# Step 9: Check Airflow
Write-Host "`n9️⃣  Checking Airflow..." -ForegroundColor Cyan
try {
    $airflowHealth = Invoke-WebRequest -Uri "http://localhost:8080/health" -ErrorAction Stop
    if ($airflowHealth.StatusCode -eq 200) {
        Write-Host "   ✅ Airflow is accessible" -ForegroundColor Green
        Write-Host "   🌐 UI: http://localhost:8080 (airflow/airflow)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ❌ Airflow not accessible at http://localhost:8080" -ForegroundColor Red
}

# Summary
Write-Host "`n" + "=" * 60
Write-Host "✅ Test Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Access Your Services:" -ForegroundColor Yellow
Write-Host "   • API:              http://localhost:8000" -ForegroundColor White
Write-Host "   • API Docs:         http://localhost:8000/docs" -ForegroundColor White
Write-Host "   • Prometheus:       http://localhost:9090" -ForegroundColor White
Write-Host "   • Grafana:          http://localhost:3000 (admin/admin)" -ForegroundColor White
Write-Host "   • Airflow:          http://localhost:8080 (airflow/airflow)" -ForegroundColor White
Write-Host "   • MinIO Console:    http://localhost:9001 (minioadmin/minioadmin)" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Check Grafana Dashboard for real-time metrics" -ForegroundColor White
Write-Host "   2. Run Airflow DAG to test ETL pipeline" -ForegroundColor White
Write-Host "   3. Make API predictions to generate latency metrics" -ForegroundColor White
Write-Host "   4. Check Prometheus queries for detailed metrics" -ForegroundColor White
Write-Host ""
Write-Host "📖 Full Testing Guide: See COMPLETE_PIPELINE_TEST.md" -ForegroundColor Cyan


