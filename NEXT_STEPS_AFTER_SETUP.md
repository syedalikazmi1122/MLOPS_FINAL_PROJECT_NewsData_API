# 🚀 Next Steps - Test Your Setup

## ✅ What You've Completed

- ✅ GitHub repository created
- ✅ Three branches created (dev, test, master)
- ✅ Branch protection rules configured
- ✅ Docker Hub account and repository created
- ✅ GitHub secrets added (DOCKER_HUB_USERNAME, DOCKER_HUB_TOKEN)
- ✅ All checks configured

## 🎯 What to Do Next (30 minutes)

### Step 1: Test Manual Docker Hub Push (10 minutes)

Test that Docker Hub credentials work:

```powershell
# 1. Login to Docker Hub
docker login

# Enter your Docker Hub username and password/token when prompted

# 2. Build the API image
docker build -f Dockerfile.api -t YOUR_USERNAME/earthquake-prediction-api:latest .

# 3. Push to Docker Hub
docker push YOUR_USERNAME/earthquake-prediction-api:latest

# 4. Verify on Docker Hub
# Go to: https://hub.docker.com/r/YOUR_USERNAME/earthquake-prediction-api
# You should see your image!
```

**Expected Result**: ✅ Image appears on Docker Hub

**If it fails**: Check your Docker Hub credentials

---

### Step 2: Commit and Push GitHub Actions Workflow (5 minutes)

The workflow file is already created, but you need to commit it:

```powershell
# 1. Check current branch
git branch

# 2. Make sure you're on test or master branch
git checkout test

# 3. Add the workflow file
git add .github/workflows/docker-build-push.yml

# 4. Commit
git commit -m "Add Docker build and push workflow"

# 5. Push to test branch
git push origin test
```

**Expected Result**: 
- ✅ Workflow file is committed
- ✅ Push succeeds
- ✅ GitHub Actions workflow should trigger automatically

---

### Step 3: Verify GitHub Actions Workflow Runs (5 minutes)

1. **Go to your GitHub repository**
2. **Click "Actions" tab** (top navigation)
3. **You should see**:
   - Workflow run: "Build and Push Docker Image"
   - Status: Yellow (running) or Green (success) or Red (failed)

4. **Click on the workflow run** to see details:
   - Checkout code
   - Set up Docker Buildx
   - Login to Docker Hub
   - Build and push Docker image

**Expected Result**: ✅ Workflow runs successfully

**If it fails**: 
- Check GitHub secrets are correct
- Check Docker Hub repository name matches
- Check workflow logs for errors

---

### Step 4: Verify Docker Hub Image (5 minutes)

1. **Go to Docker Hub**: https://hub.docker.com/r/YOUR_USERNAME/earthquake-prediction-api
2. **Check Tags**:
   - Should see: `test` (or `master` if you pushed to master)
   - Should see: `test-<SHA>` (commit hash tag)

3. **Test Pull**:
   ```powershell
   docker pull YOUR_USERNAME/earthquake-prediction-api:test
   ```

**Expected Result**: ✅ Image is on Docker Hub with correct tags

---

### Step 5: Test Branch Protection (5 minutes)

Test that branch protection is working:

```powershell
# 1. Try to push directly to test branch (should fail)
git checkout test
echo "# Test" >> test-direct-push.txt
git add test-direct-push.txt
git commit -m "Test direct push"
git push origin test
```

**Expected Result**: ❌ **Should be rejected** with error:
```
! [remote rejected] test -> test (protected branch hook declined)
```

**If it works**: Branch protection isn't fully configured (check "Do not allow bypassing")

---

### Step 6: Test PR Workflow (5 minutes)

1. **Create a feature branch**:
   ```powershell
   git checkout -b feature/test-pr
   echo "# Test PR" >> test-pr.txt
   git add test-pr.txt
   git commit -m "Test: Create PR"
   git push origin feature/test-pr
   ```

2. **Create PR on GitHub**:
   - Go to your repository
   - Click "Pull requests" → "New pull request"
   - Base: `test`, Compare: `feature/test-pr`
   - Click "Create pull request"

3. **Verify PR Requirements**:
   - Should show: "1 approval required"
   - Should show: "Required status checks" (after workflow runs)
   - Should NOT allow merge without approval

**Expected Result**: ✅ PR requires approval and status checks

---

## 📊 Verification Checklist

After completing all steps:

### Docker Hub:
- [ ] Manual push successful
- [ ] Image visible on Docker Hub
- [ ] Can pull image

### GitHub Actions:
- [ ] Workflow file committed
- [ ] Workflow runs on push to test/master
- [ ] Image pushed to Docker Hub automatically
- [ ] Tags created correctly (branch name, SHA)

### Branch Protection:
- [ ] Cannot push directly to test branch
- [ ] Cannot push directly to master branch
- [ ] PRs require approval
- [ ] PRs show status checks

---

## 🎯 Quick Test Commands

### Test 1: Manual Docker Push
```powershell
docker login
docker build -f Dockerfile.api -t YOUR_USERNAME/earthquake-prediction-api:latest .
docker push YOUR_USERNAME/earthquake-prediction-api:latest
```

### Test 2: Commit Workflow
```powershell
git add .github/workflows/docker-build-push.yml
git commit -m "Add Docker build workflow"
git push origin test
```

### Test 3: Branch Protection
```powershell
git checkout test
echo "test" >> test.txt
git add test.txt
git commit -m "Test"
git push origin test
# Expected: ❌ Rejected
```

### Test 4: PR Workflow
```powershell
git checkout -b feature/test
echo "test" >> test.txt
git add test.txt
git commit -m "Test PR"
git push origin feature/test
# Then create PR on GitHub
```

---

## 🚨 Troubleshooting

### Issue: "Workflow not running"

**Solution**:
- Check workflow file is committed
- Check you pushed to `test` or `master` branch
- Check Actions tab is enabled

### Issue: "Docker push fails in workflow"

**Solution**:
- Verify GitHub secrets are correct
- Check Docker Hub repository name matches
- Check token has write permissions

### Issue: "Can still push directly to branch"

**Solution**:
- Check "Do not allow bypassing" is enabled
- Verify rule is saved
- Try pushing again

### Issue: "Status checks not showing"

**Solution**:
- This is normal! Status checks appear after workflow runs
- Wait for workflow to complete
- Then add status checks to branch protection

---

## 🎉 Success Indicators

You'll know everything is working when:

✅ **Docker Hub**: Image appears after workflow runs  
✅ **GitHub Actions**: Workflow runs automatically on push  
✅ **Branch Protection**: Direct pushes are rejected  
✅ **PRs**: Require approval and show status checks  

---

## 📝 Next: Add Status Checks to Branch Protection

After your workflow runs successfully:

1. **Go to**: Settings → Branches
2. **Edit your branch protection rule**
3. **Under "Require status checks"**:
   - You'll now see available checks (like "build-and-push")
   - Check the boxes for checks you want to require
   - Save changes

---

## 🚀 After Everything Works

Once verified:

1. **Create a real PR**:
   - Make actual code changes
   - Create PR to `test` branch
   - Get approval
   - Merge

2. **Watch the pipeline**:
   - PR merged → Workflow runs → Image pushed to Docker Hub

3. **Move to master**:
   - Create PR from `test` to `master`
   - Requires 2 approvals
   - Merge when ready

---

**Follow these steps in order, and you'll have a fully working CI/CD pipeline!** 🎯

