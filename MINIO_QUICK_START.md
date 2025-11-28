# MinIO Quick Start Guide

## Why MinIO?
- ✅ **Free** - No costs, open-source
- ✅ **S3-Compatible** - Works with DVC's S3 support
- ✅ **Local** - Run on your machine, no cloud needed
- ✅ **Fast** - Local storage is faster than cloud

## Quick Setup (5 minutes)

### Step 1: Start MinIO with Docker

```powershell
# Option A: Use docker-compose (easiest)
docker-compose up -d

# Option B: Manual Docker command
docker run -d `
  -p 9000:9000 `
  -p 9001:9001 `
  --name minio `
  -v ${PWD}\minio-data:/data `
  -e "MINIO_ROOT_USER=minioadmin" `
  -e "MINIO_ROOT_PASSWORD=minioadmin" `
  minio/minio server /data --console-address ":9001"
```

### Step 2: Access MinIO Console

1. Open browser: **http://localhost:9001**
2. Login:
   - Username: `minioadmin`
   - Password: `minioadmin`
3. Click **"Create Bucket"**
4. Name it: `earthquake-data`
5. Set as **Private** (recommended)

### Step 3: Configure DVC

```powershell
# Configure DVC to use MinIO
python -m dvc remote add -d minio-storage s3://earthquake-data
python -m dvc remote modify minio-storage endpointurl http://localhost:9000
python -m dvc remote modify minio-storage access_key_id minioadmin
python -m dvc remote modify minio-storage secret_access_key minioadmin

# Verify
python -m dvc remote list
```

### Step 4: Test Push

```powershell
# Push your data to MinIO
python -m dvc push

# Check MinIO Console - you should see your files!
```

## Verify It Works

1. **Check MinIO Console**: http://localhost:9001
   - Go to "Buckets" → "earthquake-data"
   - You should see your data files

2. **Test Pull**:
   ```powershell
   # Remove local data (optional test)
   Remove-Item data\processed\earthquakes_processed.parquet
   
   # Pull from MinIO
   python -m dvc pull
   
   # File should be restored!
   ```

## Daily Usage

### Start MinIO
```powershell
docker start minio
# Or: docker-compose up -d
```

### Stop MinIO
```powershell
docker stop minio
# Or: docker-compose down
```

### Push Data
```powershell
python -m dvc push
```

### Pull Data
```powershell
python -m dvc pull
```

## Troubleshooting

### MinIO won't start
```powershell
# Check if port is in use
netstat -ano | findstr :9000

# Remove old container
docker rm -f minio

# Start fresh
docker-compose up -d
```

### DVC push fails
- Ensure MinIO is running: `docker ps`
- Check bucket exists in MinIO Console
- Verify credentials match

### Can't access console
- Try: http://127.0.0.1:9001
- Check firewall settings
- Verify Docker is running

## Data Location

Your data is stored in: `./minio-data/` directory

**Backup**: Just copy the `minio-data` folder!

## Next Steps

Once MinIO is set up:
1. ✅ Data versioning complete
2. ✅ Ready for Airflow DAG integration
3. ✅ Can proceed to Phase III (CI/CD)

