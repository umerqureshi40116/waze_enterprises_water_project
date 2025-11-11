# Step-by-Step Guide: Set ENVIRONMENT=production on Render

## Method 1: Using Render Dashboard (RECOMMENDED - Easiest)

### Step 1: Go to Render Dashboard
1. Open https://dashboard.render.com
2. Sign in with your GitHub account

### Step 2: Select Your Backend Service
1. On the left sidebar, click **"Services"**
2. Find and click on your backend service (name should be something like `waze-enterprises-water-project-backend`)

### Step 3: Open Environment Settings
1. In the service detail page, find the left sidebar menu
2. Click on **"Environment"** (or look for "Settings" → "Environment")
3. You should see a section called **"Environment Variables"**

### Step 4: Add the Environment Variable
1. Click the **"Add Environment Variable"** button (or **"+"** button)
2. Fill in the form:
   - **Key:** `ENVIRONMENT`
   - **Value:** `production`
3. Click **"Save"** or **"Add"**

### Step 5: Redeploy (Automatic)
- Render will automatically redeploy your service with the new environment variable
- Wait 2-3 minutes for the deployment to complete
- You'll see a status indicator showing "Deployed" when done

---

## Method 2: Using Render.yaml (For Git-based Configuration)

If you want to track this in git, create/update `render.yaml`:

### Step 1: Update render.yaml
Create or edit `render.yaml` in your project root:

```yaml
services:
  - type: web
    name: waze-enterprises-water-project-backend
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        scope: build
        sync: false
      - key: ENVIRONMENT
        value: production
      - key: SECRET_KEY
        scope: build
        sync: false
```

### Step 2: Push to GitHub
```bash
git add render.yaml
git commit -m "Add render.yaml with production environment variable"
git push origin master
```

### Step 3: Redeploy
- Go to Render Dashboard
- Click on your service
- Click **"Manual Deploy"** → **"Deploy Latest Commit"**

---

## Method 3: Using Render CLI (If You Have CLI Access)

```bash
# Login to Render
render login

# Set environment variable
render env set ENVIRONMENT production --service waze-enterprises-water-project-backend

# Deploy
render deploy --service waze-enterprises-water-project-backend
```

---

## Screenshots Reference

Here's what you're looking for in Render Dashboard:

```
┌─ Dashboard ─────────────────────────────────┐
│  Services                                    │
│  ├─ waze-enterprises-water-project-backend  │ ← Click here
│  │  ├─ Deploys                              │
│  │  ├─ Events                               │
│  │  ├─ Analytics                            │
│  │  ├─ Settings                             │
│  │  ├─ Environment  ←─────┐                 │
│  │  │                      │ Click here      │
│  │  ├─ Notifications       │                 │
│  │  └─ etc.               │                 │
│                            │                 │
│  Environment Variables:   │                 │
│  ┌─────────────────────┐  │                 │
│  │ Key    │ Value      │  │                 │
│  ├─────────────────────┤  │                 │
│  │ DATABASE_URL (set) │ ◄─┘                 │
│  ├─────────────────────┤                    │
│  │ ENVIRONMENT (ADD)   │ ← Add here         │
│  │ [+] Add             │                    │
│  └─────────────────────┘                    │
└─────────────────────────────────────────────┘
```

---

## Verification Steps

After adding the environment variable:

### 1. Check if it was set correctly
Go to your service → Environment → Look for ENVIRONMENT = production

### 2. Wait for auto-redeploy
- Status will show "Building..." then "Deploying..." then "Deployed"
- Takes about 2-3 minutes

### 3. Test the backend
Once deployed, test:
```bash
curl https://waze-enterprises-water-project-backend.onrender.com/config
```

You should see:
```json
{
  "environment": "production",
  "database_url_set": true,
  "database_url_preview": "postgresql://..."
}
```

### 4. Test the app
Visit your frontend and check the browser console - you should see:
```
✅ Keep-alive ping sent to backend
```

Every 10 minutes you'll see this message, which means the keep-alive is working!

---

## Common Issues & Solutions

### Issue: Environment variable not appearing after save
**Solution:** Wait 30 seconds, refresh the page, and check again

### Issue: Service still shows "Deploying..." after 10 minutes
**Solution:** 
1. Click on "Events" tab to see what's happening
2. Check "Logs" for any build errors
3. If stuck, click "Cancel Deploy" and try "Manual Deploy" again

### Issue: Unsure which service is your backend
**Solution:** 
Click on a service and check the URL - it should contain "water-project-backend"

### Issue: Multiple services showing
**Solution:**
- Backend service URL: `...water-project-backend.onrender.com`
- Frontend service URL: `...water-project.onrender.com` (without "-backend")

---

## Next Steps After This Step

1. ✅ Set ENVIRONMENT=production ← YOU ARE HERE
2. ⏳ Wait for Render to redeploy (2-3 min)
3. ⏳ Run SQL migration on Neon database
4. ✅ Test the app

---

## Questions?

If you get stuck:
- Post a screenshot of your Render dashboard
- Describe what error you see
- I'll help guide you through it!
