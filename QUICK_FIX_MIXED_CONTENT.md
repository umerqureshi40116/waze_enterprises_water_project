# QUICK CHECKLIST - WHY YOU'RE GETTING MIXED CONTENT ERROR

## The Error
```
Mixed Content: ... requested an insecure XMLHttpRequest endpoint 'http://...'
```

## Root Cause
**Vercel environment variable `VITE_API_BASE_URL` is NOT SET**

- ✅ Your `.env.production` file is correct
- ✅ Your axios.js has correct logic
- ❌ Vercel Dashboard is missing the env variable
- ❌ So it's using old fallback value (HTTP)

---

## 3-MINUTE FIX

1. **Go to:** https://vercel.com/dashboard
2. **Click:** Your project (waze-enterprises-inventory)
3. **Click:** Settings (top menu)
4. **Click:** Environment Variables (left sidebar)
5. **Click:** Add New
6. **Fill in:**
   ```
   Name:  VITE_API_BASE_URL
   Value: https://wazeenterpriseswaterproject-production.up.railway.app/api/v1
   ```
7. **Set:** Environment = Production
8. **Click:** Save
9. **Click:** Deployments (top menu)
10. **Click:** Latest deployment
11. **Click:** ... → Redeploy
12. **Wait:** 2-3 minutes for "Ready"
13. **Refresh** your frontend
14. **Test** creating a purchase

---

## WHAT YOU'LL SEE IF IT WORKS

DevTools Console (F12 → Console) will show:
```
📡 FINAL API Base URL: https://wazeenterpriseswaterproject-production.up.railway.app/api/v1
✅ Already HTTPS or localhost - no conversion needed
```

---

## IF STILL NOT WORKING

**Option 1: Check Vercel Variable is Set**
- Vercel Dashboard → Settings → Environment Variables
- Look for: `VITE_API_BASE_URL`
- Should show: `https://wazeenterpriseswaterproject-production.up.railway.app/api/v1`
- If missing, add it

**Option 2: Hard Refresh Browser**
```
Ctrl + Shift + R  (Windows)
Cmd + Shift + R   (Mac)
```

**Option 3: Check Backend is Running**
```bash
curl https://wazeenterpriseswaterproject-production.up.railway.app/api/docs
# Should return HTML page (not error)
```

If backend returns 404 or timeout, backend is down.

---

## SUMMARY

You have all the code in place. You just need to:

1. Set environment variable in Vercel Dashboard
2. Redeploy
3. Clear browser cache
4. Test

That's it! The mixed content error will disappear.

