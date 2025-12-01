# MinIO Integration Guide - Complete Setup

This guide walks you through setting up MinIO with Docker and integrating it with your MLOps pipeline.

## 📋 Overview

According to the project requirements:
- **Processed datasets must be stored in cloud-like object storage** (MinIO, S3, Azure Blob)
- **Data must be versioned with DVC** and pushed to remote storage
- **MinIO is S3-compatible**, so it works seamlessly with DVC's S3 support

## 🚀 Quick Start (5 Minutes)

### Step 1: Start MinIO with Docker

```powershell
# Make sure Docker Desktop is running, then:
docker-compose up -d
```

This will:
- Pull the MinIO image (if not already present)
- Start MinIO on ports 9000 (API) and 9001 (Console)
- Create a persistent volume at `./minio-data`

**Verify it's running:**
```powershell
docker ps
# You should see a container named "minio"
```

### Step 2: Access MinIO Console

1. Open browser: **http://localhost:9001**
2. Login with:
   - Username: `minioadmin`
   - Password: `minioadmin`
3. Click **"Create Bucket"**
4. Name it: `earthquake-data`
5. Set as **Private** (recommended)

### Step 3: Install Dependencies

```powershell
# Activate your virtual environment first
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# or: source venv/bin/activate  # Linux/Mac

# Install boto3 for MinIO access
pip install -r requirements.txt
```

### Step 4: Configure DVC with MinIO

```powershell
# Initialize DVC (if not already done)
python -m dvc init

# Add MinIO as remote storage
python -m dvc remote add -d minio-storage s3://earthquake-data

# Configure MinIO endpoint and credentials
python -m dvc remote modify minio-storage endpointurl http://localhost:9000
python -m dvc remote modify minio-storage access_key_id minioadmin
python -m dvc remote modify minio-storage secret_access_key minioadmin

# Verify configuration
python -m dvc remote list
```

### Step 5: Test the Integration

```powershell
# Test direct upload to MinIO
python etl/upload_to_minio.py --file data/processed/earthquakes_processed.parquet

# Test DVC push to MinIO
python -m dvc add data/processed/earthquakes_processed.parquet
python -m dvc push

# Check MinIO Console - you should see your files!
```

## 📁 Project Structure

After setup, your data flow will be:

```
1. Extract → data/raw/earthquakes_combined.geojson
2. Quality Check → Validates data
3. Transform → data/processed/earthquakes_processed_YYYYMMDD.parquet
4. Upload to MinIO → s3://earthquake-data/processed/...
5. Version with DVC → Tracks metadata + pushes to MinIO
```

## 🔧 Airflow DAG Integration

The DAG (`dags/earthquake_etl_dag.py`) now includes:

1. **Upload Task**: Uploads processed data directly to MinIO
2. **Version Task**: Uses DVC to version and push to MinIO

### Environment Variables (Optional)

You can override MinIO settings via environment variables:

```powershell
# Set in your environment or .env file
$env:MINIO_ENDPOINT = "http://localhost:9000"
$env:MINIO_ACCESS_KEY = "minioadmin"
$env:MINIO_SECRET_KEY = "minioadmin"
$env:MINIO_BUCKET = "earthquake-data"
```

## 🧪 Manual Testing

### Test Direct Upload

```powershell
python etl/upload_to_minio.py `
  --file data/processed/earthquakes_processed.parquet `
  --bucket earthquake-data `
  --endpoint http://localhost:9000
```

### Test DVC Integration

```powershell
# Add file to DVC tracking
python -m dvc add data/processed/earthquakes_processed.parquet

# Push to MinIO
python -m dvc push

# Verify in MinIO Console
# Files should appear in: earthquake-data/data/processed/
```

### Test Full Pipeline

```powershell
# Run ETL steps manually
python etl/download_historical.py --start-year 2018 --end-year 2020 --combine
python etl/data_quality_check.py --input data/raw/earthquakes_combined.geojson
python etl/transform_data.py --input data/raw/earthquakes_combined.geojson --output data/processed/test.parquet

# Upload to MinIO
python etl/upload_to_minio.py --file data/processed/test.parquet

# Version with DVC
python -m dvc add data/processed/test.parquet
python -m dvc push
```

## 🔍 Verification Checklist

- [ ] MinIO container is running (`docker ps`)
- [ ] MinIO Console accessible (http://localhost:9001)
- [ ] Bucket `earthquake-data` created
- [ ] DVC remote configured (`dvc remote list`)
- [ ] Test upload successful (check MinIO Console)
- [ ] DVC push successful (files visible in MinIO)

## 🐛 Troubleshooting

### MinIO Not Starting

```powershell
# Check Docker Desktop is running
# Check if port 9000/9001 are already in use
netstat -ano | findstr :9000

# View MinIO logs
docker logs minio
```

### DVC Push Fails

**Error: "No remote configured"**
```powershell
# Re-run DVC remote setup
python -m dvc remote add -d minio-storage s3://earthquake-data
python -m dvc remote modify minio-storage endpointurl http://localhost:9000
python -m dvc remote modify minio-storage access_key_id minioadmin
python -m dvc remote modify minio-storage secret_access_key minioadmin
```

**Error: "Connection refused"**
- Ensure MinIO is running: `docker ps`
- Check endpoint URL is correct: `http://localhost:9000`
- Verify bucket exists in MinIO Console

**Error: "Access Denied"**
- Verify credentials: `minioadmin` / `minioadmin`
- Check bucket permissions in MinIO Console
- Ensure bucket name matches: `earthquake-data`

### Upload Script Fails

**Error: "Credentials not found"**
```powershell
# Set environment variables
$env:MINIO_ACCESS_KEY = "minioadmin"
$env:MINIO_SECRET_KEY = "minioadmin"
$env:MINIO_ENDPOINT = "http://localhost:9000"
```

**Error: "Bucket not found"**
- Create bucket in MinIO Console first
- Or the script will auto-create it (if permissions allow)

## 📊 Monitoring MinIO

### View Files in MinIO Console

1. Go to http://localhost:9001
2. Navigate to **Buckets** → **earthquake-data**
3. Browse folders: `processed/` (direct uploads), `data/processed/` (DVC files)

### MinIO Storage Location

Data is stored in: `./minio-data/` (persistent volume)

**Backup MinIO data:**
```powershell
# Stop MinIO
docker-compose down

# Backup the data directory
Copy-Item -Recurse .\minio-data .\minio-data-backup

# Restart MinIO
docker-compose up -d
```

## 🔐 Security Considerations

### For Production:

1. **Change default credentials:**
   ```yaml
   # In docker-compose.yml
   environment:
     MINIO_ROOT_USER: your-secure-username
     MINIO_ROOT_PASSWORD: your-secure-password
   ```

2. **Use environment variables:**
   ```powershell
   # Create .env file (don't commit to Git!)
   MINIO_ROOT_USER=secure_user
   MINIO_ROOT_PASSWORD=secure_password
   ```

3. **Enable HTTPS** (requires SSL certificates)

4. **Set up access policies** in MinIO Console

## 📝 Daily Usage

### Start MinIO
```powershell
docker-compose up -d
# or
docker start minio
```

### Stop MinIO
```powershell
docker-compose down
# or
docker stop minio
```

### View Logs
```powershell
docker logs minio
docker logs -f minio  # Follow logs
```

## ✅ Integration Complete!

Your pipeline now:
- ✅ Stores processed data in MinIO (object storage)
- ✅ Versions data with DVC
- ✅ Pushes DVC data to MinIO remote
- ✅ Integrates with Airflow DAG automatically

**Next Steps:**
- Test the full Airflow DAG
- Set up Dagshub for MLflow tracking (Phase II)
- Configure CI/CD pipeline (Phase III)

## 📚 Additional Resources

- [MinIO Documentation](https://min.io/docs/)
- [DVC S3 Remote](https://dvc.org/doc/user-guide/data-management/remote-storage/s3)
- [boto3 S3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)

