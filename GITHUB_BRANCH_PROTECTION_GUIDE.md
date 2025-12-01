# 🔒 GitHub Branch Protection Rules & PR Requirements Guide

## 📋 Overview

This guide shows you how to set up branch protection rules and PR requirements for your MLOps pipeline with three branches:
- **dev** - Development branch
- **test** - Testing/staging branch  
- **master** (or **main**) - Production branch

## 🎯 Branch Strategy

```
feature → dev → test → master
```

- **feature branches**: Individual features/PRs
- **dev**: Development integration
- **test**: Staging/testing environment
- **master**: Production (protected)

---

## 🔧 Step-by-Step Setup

### Step 1: Access Branch Protection Settings

1. **Go to your GitHub repository**
2. **Click "Settings"** (top navigation)
3. **Click "Branches"** (left sidebar)
4. **Click "Add rule"** or edit existing rules

### Step 2: Configure Branch Protection for `master` Branch

**Rule name**: `master` (or `main`)

#### Required Settings:

1. **✅ Protect matching branches**
   - Branch name pattern: `master` (or `main`)

2. **✅ Require a pull request before merging**
   - ✅ Require approvals: **2** (or 1 for solo projects)
   - ✅ Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require review from Code Owners (if you have CODEOWNERS file)

3. **✅ Require status checks to pass before merging**
   - ✅ Require branches to be up to date before merging
   - Select status checks:
     - `lint` (if you have linting workflow)
     - `test` (if you have testing workflow)
     - `build` (if you have build workflow)
   - ⚠️ **Note**: Status checks appear after you create GitHub Actions workflows

4. **✅ Require conversation resolution before merging**
   - All comments must be resolved

5. **✅ Do not allow bypassing the above settings**
   - Even admins must follow these rules

6. **✅ Restrict who can push to matching branches**
   - No one can push directly (must use PRs)

7. **✅ Allow force pushes**: ❌ **Unchecked**
   - Prevents force pushes

8. **✅ Allow deletions**: ❌ **Unchecked**
   - Prevents branch deletion

**Click "Create"** to save the rule.

### Step 3: Configure Branch Protection for `test` Branch

**Rule name**: `test`

#### Required Settings:

1. **✅ Protect matching branches**
   - Branch name pattern: `test`

2. **✅ Require a pull request before merging**
   - ✅ Require approvals: **1**
   - ✅ Dismiss stale approvals when new commits are pushed

3. **✅ Require status checks to pass before merging**
   - ✅ Require branches to be up to date
   - Select status checks:
     - `lint`
     - `test`
     - `model-retrain` (if you have model retraining workflow)

4. **✅ Require conversation resolution before merging**

5. **✅ Do not allow bypassing**

6. **✅ Restrict pushes**: Only via PRs

7. **❌ Allow force pushes**: Unchecked

8. **❌ Allow deletions**: Unchecked

**Click "Create"** to save.

### Step 4: Configure Branch Protection for `dev` Branch (Optional but Recommended)

**Rule name**: `dev`

#### Settings (Less Strict):

1. **✅ Protect matching branches**
   - Branch name pattern: `dev`

2. **✅ Require a pull request before merging**
   - ✅ Require approvals: **1** (or 0 for solo projects)

3. **✅ Require status checks** (optional)
   - `lint` (basic checks)

4. **❌ Allow force pushes**: Unchecked

5. **❌ Allow deletions**: Unchecked

**Click "Create"** to save.

---

## 📝 PR Requirements Summary

### For `master` Branch:
- ✅ **2 approvals** required
- ✅ **Status checks must pass** (lint, test, build)
- ✅ **Branches must be up to date**
- ✅ **All conversations resolved**
- ✅ **No direct pushes** (PRs only)
- ✅ **No force pushes**

### For `test` Branch:
- ✅ **1 approval** required
- ✅ **Status checks must pass** (lint, test, model-retrain)
- ✅ **Branches must be up to date**
- ✅ **All conversations resolved**
- ✅ **No direct pushes**

### For `dev` Branch:
- ✅ **1 approval** (or 0 for solo)
- ✅ **Basic status checks** (lint)
- ✅ **No direct pushes**

---

## 🎯 Visual Guide

### Branch Protection Rule Configuration:

```
┌─────────────────────────────────────────┐
│ Branch protection rule                   │
├─────────────────────────────────────────┤
│ Branch name pattern: master             │
│                                         │
│ ☑ Protect matching branches            │
│                                         │
│ ☑ Require a pull request before merging │
│   └─ ☑ Require approvals: 2            │
│   └─ ☑ Dismiss stale approvals         │
│                                         │
│ ☑ Require status checks to pass        │
│   └─ ☑ Require branches up to date     │
│   └─ ☐ lint                            │
│   └─ ☐ test                            │
│   └─ ☐ build                           │
│                                         │
│ ☑ Require conversation resolution      │
│                                         │
│ ☑ Do not allow bypassing               │
│                                         │
│ ☑ Restrict pushes                      │
│                                         │
│ ☐ Allow force pushes                   │
│ ☐ Allow deletions                      │
└─────────────────────────────────────────┘
```

---

## 🔍 How to Verify

### Test Branch Protection:

1. **Try to push directly to master**:
   ```bash
   git checkout master
   git push origin master
   ```
   **Expected**: ❌ Rejected (if protection is working)

2. **Create a PR to master**:
   - Create feature branch
   - Make changes
   - Push and create PR
   - **Expected**: PR shows "Required approvals: 2"

3. **Check PR status**:
   - PR should show required checks
   - Cannot merge until checks pass and approvals received

---

## 📋 Quick Checklist

### Master Branch:
- [ ] Branch protection enabled
- [ ] Require PR before merging
- [ ] Require 2 approvals
- [ ] Require status checks
- [ ] No direct pushes
- [ ] No force pushes
- [ ] No deletions

### Test Branch:
- [ ] Branch protection enabled
- [ ] Require PR before merging
- [ ] Require 1 approval
- [ ] Require status checks
- [ ] No direct pushes

### Dev Branch:
- [ ] Branch protection enabled (optional)
- [ ] Require PR (optional)
- [ ] Basic checks

---

## 🚨 Important Notes

1. **Status Checks**: These only appear after you create GitHub Actions workflows. You can add them later.

2. **Code Owners**: Create a `CODEOWNERS` file in `.github/` to automatically request reviews from specific people.

3. **Admin Override**: If you check "Do not allow bypassing", even admins must follow rules.

4. **Solo Projects**: For solo projects, you can set approvals to 1 or use "Allow specified actors to bypass" for yourself.

---

## 📚 Additional Resources

- [GitHub Branch Protection Docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [PR Requirements](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule)

---

**Once set up, your branches are protected and ready for CI/CD workflows!** 🔒

