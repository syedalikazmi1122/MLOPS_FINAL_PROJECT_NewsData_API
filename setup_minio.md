# MinIO Setup Guide for DVC Storage

MinIO is a free, S3-compatible object storage server. Perfect for local development and testing!

## Option 1: Local MinIO (Recommended for Development)

### Using Docker (Easiest)

```powershell
# Pull MinIO image
docker pull minio/minio

# Run MinIO server
docker run -d `
  -p 9000:9000 `
  -p 9001:9001 `
  --name minio `
  -v D:\minio-data:/data `
  -e "MINIO_ROOT_USER=minioadmin" `
  -e "MINIO_ROOT_PASSWORD=minioadmin" `
  minio/minio server /data --console-address ":9001"
```

**Access:**
- MinIO Console: http://localhost:9001
- Login: `minioadmin` / `minioadmin`
- API Endpoint: http://localhost:9000

### Using MinIO Binary (Windows)

1. Download from: https://min.io/download
2. Extract and run:
```powershell
.\minio.exe server D:\minio-data --console-address ":9001"
```

## Option 2: Free Hosted MinIO (Testing)

Use the public MinIO playground (read-only for testing):
- Endpoint: `play.min.io`
- Access Key: `Q3AM3UQ867SPQQA43P2F`
- Secret Key: `zuf+tfteSlswRu7BJ86wekitnifILbZam1KYY3TG`

**Note:** This is read-only. For write access, use local MinIO.

## Step 1: Create Bucket in MinIO

1. Open MinIO Console: http://localhost:9001
2. Login with credentials
3. Click "Create Bucket"
4. Name it: `earthquake-data` (or your preferred name)
5. Set it as **Private** (recommended)

## Step 2: Configure DVC with MinIO

```powershell
# Install DVC with S3 support (already done, but MinIO uses S3 protocol)
pip install dvc[s3]

# Configure DVC remote to use MinIO
dvc remote add -d minio-storage s3://earthquake-data

# Set MinIO endpoint (local)
dvc remote modify minio-storage endpointurl http://localhost:9000

# Set credentials
dvc remote modify minio-storage access_key_id minioadmin
dvc remote modify minio-storage secret_access_key minioadmin

# Verify configuration
dvc remote list
```

## Step 3: Test DVC with MinIO

```powershell
# Push data to MinIO
dvc push

# Verify in MinIO Console - you should see your data files

# Test pulling
dvc pull
```

## Step 4: Update Airflow DAG (Optional)

If using Airflow, update `dags/earthquake_etl_dag.py` to use MinIO:

```python
# In version_data function, add MinIO config
os.environ['AWS_ACCESS_KEY_ID'] = 'minioadmin'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'minioadmin'
os.environ['AWS_ENDPOINT_URL'] = 'http://localhost:9000'
```

## Troubleshooting

### Connection Issues
```powershell
# Test MinIO connection
aws s3 ls --endpoint-url http://localhost:9000 s3://earthquake-data
# (requires AWS CLI: pip install awscli)
```

### Permission Issues
- Ensure bucket is created and accessible
- Check credentials in MinIO Console → Access Keys

### DVC Push Fails
- Verify MinIO is running: `docker ps` or check console
- Check endpoint URL is correct
- Verify bucket name matches

## Production Considerations

For production, consider:
1. **Secure credentials** - Change default `minioadmin` password
2. **HTTPS** - Use SSL/TLS certificates
3. **Backup** - Regular backups of MinIO data directory
4. **Monitoring** - Set up MinIO metrics

## Alternative: Use MinIO in Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - ./minio-data:/data
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3
```

Run: `docker-compose up -d`

