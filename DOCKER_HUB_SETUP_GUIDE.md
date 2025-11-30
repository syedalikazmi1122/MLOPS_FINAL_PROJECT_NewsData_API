# 🐳 Docker Hub Setup & Integration Guide

## 📋 Overview

This guide shows you how to:
1. Set up Docker Hub repository
2. Push images to Docker Hub
3. Integrate with GitHub Actions for automated pushes
4. Use Docker Hub images in your deployment

---

## 🔧 Step 1: Docker Hub Repository Setup

### 1.1 Create Repository on Docker Hub

1. **Go to**: https://hub.docker.com
2. **Login** to your account
3. **Click "Repositories"** → **"Create Repository"**
4. **Fill in details**:
   - **Name**: `earthquake-prediction-api` (or your choice)
   - **Visibility**: Public (free) or Private (paid)
   - **Description**: "MLOps Earthquake Prediction Model Serving API"
5. **Click "Create"**

### 1.2 Get Docker Hub Credentials

You'll need:
- **Username**: Your Docker Hub username
- **Password/Token**: 
  - Use your Docker Hub password, OR
  - Create an access token (recommended):
    1. Go to: https://hub.docker.com/settings/security
    2. Click "New Access Token"
    3. Name: "GitHub Actions"
    4. Permissions: Read, Write, Delete
    5. **Copy the token** (you won't see it again!)

---

## 🚀 Step 2: Manual Push to Docker Hub

### 2.1 Login to Docker Hub

```powershell
# Login with your credentials
docker login

# Or with username
docker login -u YOUR_USERNAME

# Enter password when prompted
```

### 2.2 Build Your Image

```powershell
# Build the API image
docker build -f Dockerfile.api -t YOUR_USERNAME/earthquake-prediction-api:latest .

# Or with version tag
docker build -f Dockerfile.api -t YOUR_USERNAME/earthquake-prediction-api:v1.0.0 .
```

### 2.3 Tag Image for Docker Hub

```powershell
# Tag with your Docker Hub username
docker tag earthquake-prediction-api:latest YOUR_USERNAME/earthquake-prediction-api:latest

# Or if already tagged during build, skip this step
```

### 2.4 Push to Docker Hub

```powershell
# Push to Docker Hub
docker push YOUR_USERNAME/earthquake-prediction-api:latest

# Or specific version
docker push YOUR_USERNAME/earthquake-prediction-api:v1.0.0
```

### 2.5 Verify Push

1. **Go to**: https://hub.docker.com/r/YOUR_USERNAME/earthquake-prediction-api
2. **Check**: Your image should be visible
3. **Test pull**:
   ```powershell
   docker pull YOUR_USERNAME/earthquake-prediction-api:latest
   ```

---

## 🔐 Step 3: GitHub Secrets Setup

For automated pushes via GitHub Actions, you need to add secrets:

### 3.1 Add Docker Hub Secrets to GitHub

1. **Go to your GitHub repository**
2. **Click "Settings"** → **"Secrets and variables"** → **"Actions"**
3. **Click "New repository secret"**
4. **Add these secrets**:

   **Secret 1: `DOCKER_HUB_USERNAME`**
   - Name: `DOCKER_HUB_USERNAME`
   - Value: Your Docker Hub username
   - Click "Add secret"

   **Secret 2: `DOCKER_HUB_TOKEN`**
   - Name: `DOCKER_HUB_TOKEN`
   - Value: Your Docker Hub access token (or password)
   - Click "Add secret"

### 3.2 Verify Secrets

- Go to: Settings → Secrets and variables → Actions
- You should see both secrets listed

---

## 🤖 Step 4: GitHub Actions Workflow for Docker Hub

Create a workflow that automatically builds and pushes to Docker Hub:

### 4.1 Create Workflow File

Create: `.github/workflows/docker-build-push.yml`

```yaml
name: Build and Push Docker Image

on:
  push:
    branches:
      - test
      - master
    paths:
      - 'api/**'
      - 'Dockerfile.api'
      - '.github/workflows/docker-build-push.yml'
  pull_request:
    branches:
      - test
      - master
    paths:
      - 'api/**'
      - 'Dockerfile.api'

env:
  DOCKER_IMAGE_NAME: earthquake-prediction-api
  DOCKER_HUB_REPO: ${{ secrets.DOCKER_HUB_USERNAME }}/earthquake-prediction-api

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_HUB_USERNAME }}
          password: ${{ secrets.DOCKER_HUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.DOCKER_HUB_REPO }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix={{branch}}-
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile.api
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=${{ env.DOCKER_HUB_REPO }}:buildcache
          cache-to: type=registry,ref=${{ env.DOCKER_HUB_REPO }}:buildcache,mode=max
      
      - name: Image digest
        run: echo "Image pushed with digest ${{ steps.build.outputs.digest }}"
```

### 4.2 Workflow Explanation

- **Triggers**: Pushes to `test`/`master` branches or PRs
- **Builds**: Docker image from `Dockerfile.api`
- **Tags**: Automatically tags with branch name, SHA, etc.
- **Pushes**: Only pushes on actual commits (not PRs)

---

## 📋 Step 5: Using Docker Hub Images

### 5.1 Pull and Run from Docker Hub

```powershell
# Pull image
docker pull YOUR_USERNAME/earthquake-prediction-api:latest

# Run container
docker run -d \
  --name earthquake-api \
  -p 8000:8000 \
  -e MLFLOW_TRACKING_URI="https://dagshub.com/i222472/my-first-repo.mlflow" \
  -e MLFLOW_TRACKING_USERNAME="i222472" \
  -e MLFLOW_TRACKING_PASSWORD="YOUR_TOKEN" \
  YOUR_USERNAME/earthquake-prediction-api:latest
```

### 5.2 Update docker-compose.yml to Use Docker Hub Image

```yaml
  api:
    image: YOUR_USERNAME/earthquake-prediction-api:latest  # Use Docker Hub image
    # ... rest of config
```

---

## 🎯 Step 6: Version Tagging Strategy

### Recommended Tags:

- **`latest`**: Latest stable version (from `master` branch)
- **`test`**: Latest test version (from `test` branch)
- **`v1.0.0`**: Semantic versioning
- **`v1.0`**: Major.minor version
- **`master-abc123`**: Branch-SHA for specific commits

### Tagging in GitHub Actions:

The workflow above automatically creates tags based on:
- Branch name (`master`, `test`)
- Git SHA (commit hash)
- Semantic version (if you use tags)

---

## 🔍 Verification Checklist

- [ ] Docker Hub repository created
- [ ] Docker Hub credentials saved
- [ ] Manual push successful
- [ ] Image visible on Docker Hub
- [ ] GitHub secrets added (`DOCKER_HUB_USERNAME`, `DOCKER_HUB_TOKEN`)
- [ ] GitHub Actions workflow created
- [ ] Workflow runs successfully on push
- [ ] Image appears on Docker Hub after workflow

---

## 🚨 Troubleshooting

### Issue: "denied: requested access to the resource is denied"

**Solution**: 
- Check Docker Hub credentials
- Verify username matches repository owner
- Ensure token has write permissions

### Issue: "unauthorized: authentication required"

**Solution**:
- Re-login: `docker login`
- Check GitHub secrets are correct
- Verify token hasn't expired

### Issue: Workflow fails to push

**Solution**:
- Check secrets are set correctly
- Verify workflow has `push: true` (not on PRs)
- Check Docker Hub repository exists

---

## 📚 Additional Resources

- [Docker Hub Documentation](https://docs.docker.com/docker-hub/)
- [GitHub Actions Docker](https://docs.github.com/en/actions/publishing-packages/publishing-docker-images)
- [Docker Buildx](https://docs.docker.com/buildx/working-with-buildx/)

---

## 🎉 Quick Start Commands

```powershell
# 1. Login
docker login

# 2. Build
docker build -f Dockerfile.api -t YOUR_USERNAME/earthquake-prediction-api:latest .

# 3. Push
docker push YOUR_USERNAME/earthquake-prediction-api:latest

# 4. Verify
docker pull YOUR_USERNAME/earthquake-prediction-api:latest
```

---

**Your Docker Hub integration is ready! Images will be automatically pushed on every push to `test` or `master` branches.** 🐳

