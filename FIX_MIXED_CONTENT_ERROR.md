# Fix Mixed Content Error - Implementation Steps

## ISSUE
Frontend (HTTPS on Vercel) trying to reach Backend (HTTP on Railway)
- Browsers block HTTP from HTTPS for security

## SOLUTION
Update Vercel environment variables and redeploy

---

## STEP 1: Check Current Environment

✅ Your `.env.production` is correct:
```
VITE_API_BASE_URL=https://wazeenterpriseswaterproject-production.up.railway.app/api/v1
```

But Vercel might not have this set.

---

## STEP 2: Set Environment Variables in Vercel

1. Go to **https://vercel.com**
2. Select your project: `waze-enterprises-inventory`
3. Go to **Settings** → **Environment Variables**
4. Add this variable:
   ```
   Name:  VITE_API_BASE_URL
   Value: https://wazeenterpriseswaterproject-production.up.railway.app/api/v1
   ```
5. Click **Save**

---

## STEP 3: Clear Cache and Redeploy

Option A - Automatic (via GitHub push):
```bash
cd e:\water
git add .
git commit -m "Force redeploy with HTTPS backend"
git push origin main
# or
git push origin master
```

Option B - Manual (from Vercel):
1. Go to vercel.com → Your project → **Deployments**
2. Find the latest deployment
3. Click **...** (three dots) → **Redeploy**
4. Wait for deployment to complete (2-3 min)

---

## STEP 4: Verify Deployment

1. Check Vercel deployment status (should be "Ready")
2. Open frontend: https://waze-enterprises-inventory-p-git-05529c-umers-projects-edd7abcf.vercel.app
3. Open DevTools (F12) → Console
4. Look for logs showing:
   ```
   📡 FINAL API Base URL: https://wazeenterpriseswaterproject-production.up.railway.app/api/v1
   ```
5. If showing HTTP, scroll down console to see more logs
6. Try creating a purchase - should work without Mixed Content error

---

## STEP 5: If Still Not Working

### Check 1: Verify Backend is Running
```bash
curl https://wazeenterpriseswaterproject-production.up.railway.app/api/docs
# Should return HTML (not error)
```

### Check 2: Clear Browser Cache
1. DevTools (F12) → Application → Storage → Clear Site Data
2. Refresh page (Ctrl+Shift+R to hard refresh)
3. Try again

### Check 3: Check Vercel Environment Variable is Set
1. vercel.com → Project → Settings → Environment Variables
2. Look for `VITE_API_BASE_URL`
3. Should show: `https://wazeenterpriseswaterproject-production.up.railway.app/api/v1`
4. If missing, add it and redeploy

### Check 4: View Vercel Build Logs
1. vercel.com → Deployments
2. Click latest deployment
3. View logs to see if build had errors

---

## DONE ✅

After redeploy completes, mixed content error should be fixed!

Your API_URL code already has HTTPS enforcement:
```javascript
if (!isLocalhost && API_URL && API_URL.startsWith('http://')) {
  API_URL = API_URL.replace('http://', 'https://');
}
```

It just needs Vercel env vars to be set.

