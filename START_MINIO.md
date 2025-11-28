# Start MinIO - Quick Guide

## Docker Desktop Not Running?

### Step 1: Start Docker Desktop
1. Open **Docker Desktop** application
2. Wait for it to fully start (whale icon in system tray)
3. Then continue with setup

### Step 2: Start MinIO

**Option A: Using docker-compose (Recommended)**
```powershell
docker-compose up -d
```

**Option B: Manual Docker command**
```powershell
docker run -d `
  -p 9000:9000 `
  -p 9001:9001 `
  --name minio `
  -v ${PWD}\minio-data:/data `
  -e "MINIO_ROOT_USER=minioadmin" `
  -e "MINIO_ROOT_PASSWORD=minioadmin" `
  minio/minio server /data --console-address ":9001"
```

### Step 3: Configure DVC

Once MinIO is running:

```powershell
# Configure DVC
python -m dvc remote add -d minio-storage s3://earthquake-data
python -m dvc remote modify minio-storage endpointurl http://localhost:9000
python -m dvc remote modify minio-storage access_key_id minioadmin
python -m dvc remote modify minio-storage secret_access_key minioadmin

# Create bucket in MinIO Console first (http://localhost:9001)
# Then push data
python -m dvc push
```

## Alternative: MinIO Binary (No Docker)

If you don't want to use Docker:

1. Download MinIO: https://min.io/download
2. Extract to a folder
3. Run:
```powershell
.\minio.exe server D:\minio-data --console-address ":9001"
```

Then configure DVC the same way.

## Quick Checklist

- [ ] Docker Desktop is running
- [ ] MinIO container started
- [ ] MinIO Console accessible (http://localhost:9001)
- [ ] Bucket "earthquake-data" created
- [ ] DVC configured with MinIO
- [ ] Test push successful

See `MINIO_QUICK_START.md` for detailed instructions.

