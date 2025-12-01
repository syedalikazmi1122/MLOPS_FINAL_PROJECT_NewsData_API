# Generate Metrics for Grafana Dashboard
# This script makes API calls to generate metrics that will appear in the dashboard

Write-Host "🚀 Generating metrics for Grafana dashboard..." -ForegroundColor Green
Write-Host ""

# Check if API is running
Write-Host "Checking API status..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -ErrorAction Stop
    Write-Host "✅ API is running!" -ForegroundColor Green
    Write-Host "   Status: $($health.status)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ API is not accessible at http://localhost:8000" -ForegroundColor Red
    Write-Host "   Make sure API container is running: docker-compose up -d api" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Making API calls to generate metrics..." -ForegroundColor Yellow
Write-Host ""

# Generate health check metrics
Write-Host "1️⃣  Generating health check metrics (10 calls)..." -ForegroundColor Cyan
for ($i=1; $i -le 10; $i++) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -ErrorAction Stop
        Write-Host "   ✓ Call $i completed" -ForegroundColor Gray
    } catch {
        Write-Host "   ✗ Call $i failed" -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "2️⃣  Checking metrics endpoint..." -ForegroundColor Cyan
try {
    $metrics = Invoke-WebRequest -Uri "http://localhost:8000/metrics" -ErrorAction Stop
    $requestCount = ($metrics.Content -split "`n" | Select-String "api_requests_total").Count
    Write-Host "   ✅ Metrics endpoint is working!" -ForegroundColor Green
    Write-Host "   📊 Found $requestCount metric entries" -ForegroundColor Cyan
} catch {
    Write-Host "   ❌ Could not access metrics endpoint" -ForegroundColor Red
}

Write-Host ""
Write-Host "3️⃣  Checking Prometheus..." -ForegroundColor Cyan
try {
    $query = "api_requests_total"
    $promUrl = "http://localhost:9090/api/v1/query?query=$query"
    $promResponse = Invoke-RestMethod -Uri $promUrl -ErrorAction Stop
    
    if ($promResponse.data.result.Count -gt 0) {
        Write-Host "   ✅ Prometheus is scraping metrics!" -ForegroundColor Green
        Write-Host "   📊 Found $($promResponse.data.result.Count) metric series" -ForegroundColor Cyan
    } else {
        Write-Host "   ⚠️  Prometheus is running but no metrics yet (wait 10-15 seconds)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Prometheus not accessible at http://localhost:9090" -ForegroundColor Red
    Write-Host "   Make sure Prometheus is running: docker-compose up -d prometheus" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "4️⃣  Generating more traffic (20 calls with delays)..." -ForegroundColor Cyan
for ($i=1; $i -le 20; $i++) {
    try {
        Invoke-RestMethod -Uri "http://localhost:8000/health" -ErrorAction Stop | Out-Null
        if ($i % 5 -eq 0) {
            Write-Host "   ✓ $i calls completed..." -ForegroundColor Gray
        }
    } catch {
        Write-Host "   ✗ Call $i failed" -ForegroundColor Red
    }
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "✅ Metrics generation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Wait 10-15 seconds for Prometheus to scrape" -ForegroundColor White
Write-Host "   2. Open Grafana: http://localhost:3000" -ForegroundColor White
Write-Host "   3. Login: admin / admin" -ForegroundColor White
Write-Host "   4. Go to: Dashboards → Browse → 'MLOps Pipeline - Earthquake Prediction API'" -ForegroundColor White
Write-Host "   5. You should see metrics in the dashboard!" -ForegroundColor White
Write-Host ""
Write-Host "💡 Tip: Run this script again to generate more metrics" -ForegroundColor Cyan

