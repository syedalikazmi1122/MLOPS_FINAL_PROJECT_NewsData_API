# ✅ Complete Setup Checklist - GitHub & Docker Hub

## 📋 What You've Done

- ✅ Created GitHub repository
- ✅ Created three branches (dev, test, master)
- ✅ Created Docker Hub account
- ✅ Created Docker Hub repository

## 🎯 What to Do Next

### Part 1: GitHub Branch Protection (15 minutes)

1. **Go to GitHub Repository Settings**
   - Settings → Branches

2. **Set up Branch Protection for `master`**:
   - [ ] Protect matching branches: `master`
   - [ ] Require PR before merging
   - [ ] Require 2 approvals
   - [ ] Require status checks (will add after workflows)
   - [ ] No direct pushes
   - [ ] No force pushes
   - [ ] No deletions

3. **Set up Branch Protection for `test`**:
   - [ ] Protect matching branches: `test`
   - [ ] Require PR before merging
   - [ ] Require 1 approval
   - [ ] Require status checks
   - [ ] No direct pushes

4. **Set up Branch Protection for `dev`** (optional):
   - [ ] Protect matching branches: `dev`
   - [ ] Require PR (optional)
   - [ ] Basic checks

**See**: `GITHUB_BRANCH_PROTECTION_GUIDE.md` for detailed instructions

---

### Part 2: Docker Hub Setup (10 minutes)

1. **Get Docker Hub Credentials**:
   - [ ] Note your Docker Hub username
   - [ ] Create access token (or use password)
     - Go to: https://hub.docker.com/settings/security
     - Create new access token
     - Copy token

2. **Test Manual Push**:
   ```powershell
   # Login
   docker login
   
   # Build
   docker build -f Dockerfile.api -t YOUR_USERNAME/earthquake-prediction-api:latest .
   
   # Push
   docker push YOUR_USERNAME/earthquake-prediction-api:latest
   ```

3. **Verify on Docker Hub**:
   - [ ] Image appears in your repository
   - [ ] Can pull image: `docker pull YOUR_USERNAME/earthquake-prediction-api:latest`

**See**: `DOCKER_HUB_SETUP_GUIDE.md` for detailed instructions

---

### Part 3: GitHub Secrets (5 minutes)

1. **Add Docker Hub Secrets**:
   - [ ] Go to: Settings → Secrets and variables → Actions
   - [ ] Add secret: `DOCKER_HUB_USERNAME` = Your Docker Hub username
   - [ ] Add secret: `DOCKER_HUB_TOKEN` = Your Docker Hub token/password

2. **Verify Secrets**:
   - [ ] Both secrets are listed
   - [ ] Values are correct (you can't see them, but verify names)

---

### Part 4: GitHub Actions Workflow (Already Created!)

✅ **Workflow file created**: `.github/workflows/docker-build-push.yml`

**What it does**:
- Builds Docker image on push to `test` or `master`
- Pushes to Docker Hub automatically
- Tags images with branch name and SHA

**To activate**:
1. [ ] Commit and push the workflow file
2. [ ] Make a change to `api/` or `Dockerfile.api`
3. [ ] Push to `test` or `master` branch
4. [ ] Check Actions tab → Workflow should run
5. [ ] Verify image appears on Docker Hub

---

## 🎯 Quick Start Commands

### Test Branch Protection:

```powershell
# Try to push directly to master (should fail)
git checkout master
git push origin master
# Expected: ❌ Rejected
```

### Test Docker Hub Push:

```powershell
# Login
docker login

# Build and push
docker build -f Dockerfile.api -t YOUR_USERNAME/earthquake-prediction-api:latest .
docker push YOUR_USERNAME/earthquake-prediction-api:latest
```

### Test GitHub Actions:

```powershell
# Make a small change
echo "# Test" >> api/README.md

# Commit and push to test branch
git checkout test
git add .
git commit -m "Test: Trigger Docker build workflow"
git push origin test

# Check Actions tab in GitHub
```

---

## 📊 Verification Checklist

### GitHub:
- [ ] Branch protection rules set for master
- [ ] Branch protection rules set for test
- [ ] Cannot push directly to master
- [ ] PRs require approvals
- [ ] Secrets added (DOCKER_HUB_USERNAME, DOCKER_HUB_TOKEN)

### Docker Hub:
- [ ] Repository created
- [ ] Manual push successful
- [ ] Image visible on Docker Hub
- [ ] Can pull image

### GitHub Actions:
- [ ] Workflow file committed
- [ ] Workflow runs on push
- [ ] Image pushed to Docker Hub automatically
- [ ] Tags created correctly

---

## 🚨 Common Issues & Solutions

### Issue: "Cannot push to master"
**Solution**: This is expected! Use PRs instead.

### Issue: "Workflow fails: secrets not found"
**Solution**: Check secrets are added in Settings → Secrets → Actions

### Issue: "Docker push denied"
**Solution**: 
- Verify Docker Hub credentials
- Check repository name matches
- Ensure token has write permissions

### Issue: "Status checks not showing"
**Solution**: Status checks appear after workflows run. Add them to branch protection after first successful run.

---

## 📚 Documentation Files

- **`GITHUB_BRANCH_PROTECTION_GUIDE.md`** - Detailed branch protection setup
- **`DOCKER_HUB_SETUP_GUIDE.md`** - Docker Hub integration guide
- **`.github/workflows/docker-build-push.yml`** - GitHub Actions workflow

---

## 🎉 Next Steps After Setup

Once everything is set up:

1. **Create a test PR**:
   - Create feature branch
   - Make changes
   - Create PR to `dev`
   - Verify PR requirements work

2. **Test full pipeline**:
   - PR to `dev` → Merge
   - PR to `test` → Should trigger Docker build
   - PR to `master` → Should require 2 approvals

3. **Monitor Docker Hub**:
   - Check images are being pushed
   - Verify tags are correct

---

**You're all set! Follow the checklist above to complete the setup.** ✅

