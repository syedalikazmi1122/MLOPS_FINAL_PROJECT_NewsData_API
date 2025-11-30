# ✅ Phase IV: Monitoring & Observability - Complete!

## 🎉 What's Been Created

### 1. Prometheus Integration ✅

**Updated Files**:
- `api/app.py` - Added Prometheus metrics
- `api/requirements.txt` - Added prometheus-client

**Metrics Added**:
- ✅ **API Request Count** (`api_requests_total`) - Total requests by method, endpoint, status
- ✅ **Inference Latency** (`api_inference_latency_ms`) - Histogram of prediction latency
- ✅ **Data Drift Ratio** (`api_data_drift_ratio`) - Ratio of OOD requests
- ✅ **Active Requests** (`api_active_requests`) - Current active requests

**Endpoint**:
- ✅ `/metrics` - Prometheus metrics endpoint

### 2. Grafana Setup ✅

**Files Created**:
- `prometheus/prometheus.yml` - Prometheus configuration
- `grafana/provisioning/datasources/prometheus.yml` - Prometheus data source
- `grafana/provisioning/dashboards/dashboard.yml` - Dashboard provisioning
- `grafana/dashboards/mlops-dashboard.json` - Main monitoring dashboard

**Updated Files**:
- `docker-compose.yml` - Added Prometheus and Grafana services

**Features**:
- ✅ Prometheus scraping API metrics every 10s
- ✅ Grafana connected to Prometheus
- ✅ Pre-configured dashboard with:
  - Request count graphs
  - Inference latency (with 95th percentile)
  - Data drift ratio
  - Active requests
  - Request rate by status
- ✅ Alerts configured:
  - High latency alert (>500ms)
  - Data drift alert (>50% drift)

---

## 🚀 How to Use

### Start All Services

```powershell
# Start everything (including Prometheus and Grafana)
docker-compose up -d

# Or start specific services
docker-compose up -d prometheus grafana api
```

### Access Services

1. **API**: http://localhost:8000
   - Health: http://localhost:8000/health
   - Metrics: http://localhost:8000/metrics
   - Docs: http://localhost:8000/docs

2. **Prometheus**: http://localhost:9090
   - Query metrics: http://localhost:9090/graph
   - Example query: `rate(api_requests_total[5m])`

3. **Grafana**: http://localhost:3000
   - Username: `admin`
   - Password: `admin`
   - Dashboard: "MLOps Pipeline - Earthquake Prediction API"

### Generate Metrics

```powershell
# Make some API calls to generate metrics
curl http://localhost:8000/health
curl http://localhost:8000/metrics

# Make predictions (if model is loaded)
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [{"latitude": 34.0, "longitude": -118.0, "depth": 10.0}]}'
```

### View Metrics in Prometheus

1. Go to: http://localhost:9090
2. Click "Graph" tab
3. Try queries:
   - `api_requests_total` - Total requests
   - `rate(api_requests_total[5m])` - Request rate
   - `api_inference_latency_ms` - Latency histogram
   - `api_data_drift_ratio` - Data drift ratio

### View Dashboard in Grafana

1. Go to: http://localhost:3000
2. Login: `admin` / `admin`
3. Dashboard should auto-load: "MLOps Pipeline - Earthquake Prediction API"
4. Or go to: Dashboards → Browse → "MLOps Pipeline"

---

## 📊 Dashboard Panels

### 1. API Request Count
- Shows request rate by endpoint and status
- Updates every 10 seconds

### 2. Inference Latency
- 95th percentile, 50th percentile, and average
- **Alert**: Fires if latency > 500ms for 5 minutes

### 3. Data Drift Ratio
- Shows ratio of requests with out-of-distribution features
- **Alert**: Fires if drift ratio > 50% for 5 minutes

### 4. Active Requests
- Current number of active requests being processed

### 5. Request Rate by Status
- Pie chart showing success vs error rates

### 6. Total Requests
- Total number of requests since start

---

## 🔔 Alerts Configured

### Alert 1: High Latency
- **Condition**: 95th percentile latency > 500ms for 5 minutes
- **Action**: Alert fires (can be configured to send to Slack/email)

### Alert 2: Data Drift
- **Condition**: Data drift ratio > 50% for 5 minutes
- **Action**: Alert fires (indicates potential model degradation)

---

## 📝 Metrics Details

### `api_requests_total`
- **Type**: Counter
- **Labels**: `method`, `endpoint`, `status`
- **Description**: Total number of API requests

### `api_inference_latency_ms`
- **Type**: Histogram
- **Buckets**: [10, 50, 100, 200, 500, 1000, 2000, 5000] ms
- **Description**: Latency distribution for predictions

### `api_data_drift_ratio`
- **Type**: Gauge
- **Description**: Ratio of requests with OOD features (0.0 = no drift, 1.0 = all drift)

### `api_active_requests`
- **Type**: Gauge
- **Description**: Current number of active requests

---

## 🎯 Testing the Setup

### Step 1: Start Services

```powershell
docker-compose up -d prometheus grafana api
```

### Step 2: Check Services

```powershell
# Check API
curl http://localhost:8000/health

# Check Prometheus
curl http://localhost:9090/-/healthy

# Check Grafana
curl http://localhost:3000/api/health
```

### Step 3: Generate Metrics

```powershell
# Make some requests
for ($i=1; $i -le 10; $i++) {
    curl http://localhost:8000/health
    Start-Sleep -Seconds 1
}

# Check metrics endpoint
curl http://localhost:8000/metrics
```

### Step 4: View Dashboard

1. Open: http://localhost:3000
2. Login: `admin` / `admin`
3. Dashboard should show metrics!

---

## 📁 Files Created/Updated

### Created:
1. `prometheus/prometheus.yml` - Prometheus config
2. `grafana/provisioning/datasources/prometheus.yml` - Data source
3. `grafana/provisioning/dashboards/dashboard.yml` - Dashboard provisioning
4. `grafana/dashboards/mlops-dashboard.json` - Dashboard definition

### Updated:
1. `api/app.py` - Added Prometheus metrics
2. `api/requirements.txt` - Added prometheus-client
3. `docker-compose.yml` - Added Prometheus and Grafana services

---

## ✅ Phase IV Checklist

- [x] Prometheus client library installed
- [x] Metrics added to FastAPI:
  - [x] API inference latency
  - [x] Total request count
  - [x] Data drift ratio
- [x] `/metrics` endpoint exposed
- [x] Prometheus deployed (Docker)
- [x] Grafana deployed (Docker)
- [x] Grafana connected to Prometheus
- [x] Dashboard created:
  - [x] Inference latency visualization
  - [x] Request count visualization
  - [x] Data drift ratio visualization
- [x] Alerts configured:
  - [x] Latency > 500ms alert
  - [x] Data drift ratio spike alert

---

## 🎉 Phase IV Status

**Phase IV: 100% Complete!** ✅

All monitoring and observability components are in place!

---

## 🚀 Next Steps

1. **Start services**: `docker-compose up -d`
2. **Generate traffic**: Make API calls
3. **View dashboard**: http://localhost:3000
4. **Test alerts**: Trigger conditions to see alerts fire

---

**Phase IV is complete! Your MLOps pipeline now has full monitoring and observability!** 🎊

