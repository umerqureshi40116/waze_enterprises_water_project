# VERCEL ENVIRONMENT VARIABLE SETUP - Visual Guide

## Your Frontend URL
```
https://waze-enterprises-inventory-p-git-05529c-umers-projects-edd7abcf.vercel.app
```

## Your Backend URL
```
https://wazeenterpriseswaterproject-production.up.railway.app
```

---

## TO FIX THE MIXED CONTENT ERROR:

### Step 1: Go to Vercel Dashboard
```
https://vercel.com/dashboard
```

### Step 2: Find Your Project
- Look for: `waze-enterprises-inventory` (or your project name)
- Click on it

### Step 3: Go to Settings
- Click **Settings** tab at the top

### Step 4: Go to Environment Variables
- Left sidebar → **Environment Variables**

### Step 5: Add/Update Variable
- Click **Add New**
- Fill in:
  ```
  Name:  VITE_API_BASE_URL
  Value: https://wazeenterpriseswaterproject-production.up.railway.app/api/v1
  ```
- Select: **Production** (not Development)
- Click **Save**

### Step 6: Redeploy
- Go back to **Deployments** tab
- Click the latest deployment
- Click **...** (three dots) → **Redeploy**
- Wait for status to show **Ready** (2-3 minutes)

---

## VERIFY IT WORKS

1. Open frontend in browser: 
   ```
   https://waze-enterprises-inventory-p-git-05529c-umers-projects-edd7abcf.vercel.app
   ```

2. Press F12 to open DevTools

3. Go to **Console** tab

4. Look for these logs:
   ```
   📡 FINAL API Base URL: https://wazeenterpriseswaterproject-production.up.railway.app/api/v1
   ```

5. Try creating a purchase - should work without error!

---

## IF STILL GETTING MIXED CONTENT ERROR

### Option A: Hard Refresh Browser
```
Press: Ctrl + Shift + R  (Windows)
or     Cmd + Shift + R   (Mac)
```

### Option B: Clear Browser Cache
1. DevTools (F12)
2. Application → Storage
3. Click **Clear Site Data**
4. Refresh page

### Option C: Verify Backend is Running
```bash
# Test backend
curl https://wazeenterpriseswaterproject-production.up.railway.app/api/docs

# Should return HTML, not error
```

### Option D: Check Vercel Logs
1. vercel.com → Your project
2. Click latest deployment
3. Scroll down to see build logs
4. Look for errors (RED text)

---

## CODE ALREADY HANDLES THIS

Your `frontend/src/api/axios.js` already has logic to convert HTTP → HTTPS:

```javascript
if (!isLocalhost && API_URL && API_URL.startsWith('http://')) {
  API_URL = API_URL.replace('http://', 'https://');
  console.log('🔒 CONVERTED to HTTPS');
}
```

It just needs:
1. ✅ Environment variable set in Vercel
2. ✅ Frontend redeployed
3. ✅ Browser cache cleared

---

## QUICK CHECKLIST

- [ ] Went to vercel.com
- [ ] Opened `waze-enterprises-inventory` project
- [ ] Clicked Settings → Environment Variables
- [ ] Added `VITE_API_BASE_URL`
- [ ] Set value to: `https://wazeenterpriseswaterproject-production.up.railway.app/api/v1`
- [ ] Clicked Save
- [ ] Went to Deployments
- [ ] Clicked Redeploy
- [ ] Waited for "Ready" status
- [ ] Cleared browser cache (Ctrl+Shift+R)
- [ ] Tested frontend - purchases work!

---

**If you get stuck on any step, let me know!**

