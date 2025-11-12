# ⚡ Quick Deploy & Test Checklist

## Before Deploying

- [ ] All changes saved locally
- [ ] Tested locally: `python -m uvicorn app.main:app --reload`
- [ ] No Python syntax errors

---

## Deploy Steps (Render)

1. **Commit changes**:
   ```bash
   git add .
   git commit -m "Perf: Add request timing middleware and async PDF generation"
   git push origin master
   ```

2. **Render auto-deploys** (wait 2-3 minutes for build)

3. **Check deployment**:
   - Go to https://dashboard.render.com
   - Select your app
   - Wait for green "Active" status

---

## Test on Deployed App

### Test 1: Request Timing Logs
1. Open Render dashboard → your app → **Logs** tab
2. Make a request from frontend (e.g., click "Sales" page)
3. Should see logs like:
   ```
   ✅ GET /api/v1/sales completed in 0.234s (status: 200)
   ```
   OR
   ```
   🐌 SLOW REQUEST: GET /api/v1/sales took 3.45s (status: 200)
   ```

**Expected**: Most requests <1s. If you see >2s, take note of which endpoints.

### Test 2: PDF Download
1. Go to **Sales** page on deployed app
2. Click "Download PDF" on any sale
3. Should complete in <5 seconds
4. Check browser DevTools → Network tab

**Expected**: PDF request takes <5s (was blocking the event loop before)

### Test 3: Excel Export
1. Go to **Reports** page
2. Click "Export Sales Excel"
3. Should download quickly

**Expected**: Completes in <10s

### Test 4: Keep-Alive
1. Open browser DevTools (F12) → **Console** tab
2. Wait ~10 seconds
3. Should see: `✅ Keep-alive ping sent to backend`

**Expected**: Message appears every 10 minutes

---

## Performance Checklist

After deploying, check:

- [ ] Request timing logs visible in Render logs
- [ ] No 500 errors related to PDF/Excel
- [ ] Keep-alive pings showing in browser console
- [ ] PDF download <5s
- [ ] Excel export <10s
- [ ] Dashboard loads <2s
- [ ] Add Expenditure button works (no 404 errors)

---

## Immediate Actions

### If App is STILL SLOW:

1. **Check which endpoint is slow**:
   - Look in Render logs for `🐌 SLOW REQUEST`
   - Note the endpoint path and time

2. **Example**: If `/api/v1/sales` is slow:
   - Enable query logging: Add `echo=True` to `database.py`
   - Redeploy
   - Check logs for slow SQL queries
   - Add caching if repeated queries

3. **Still slow after caching?**:
   - Check Render metrics (CPU/memory usage)
   - May need to upgrade plan or optimize queries further

---

## Rollback (If Something Breaks)

```bash
git revert HEAD
git push origin master
# Render auto-deploys the revert
```

---

## Expected Performance Results

| Before | After |
|--------|-------|
| PDF download: blocks other requests | PDF download: non-blocking |
| Unknown slow endpoints | Visible in logs: `🐌 SLOW REQUEST` |
| 404 errors after inactivity | ✅ Keep-alive prevents spin-down |
| Can't debug slowness | Timing logs show exact duration |

---

## Next Optimization Phases

**Phase 2** (If needed):
- Enable SQLAlchemy query logging
- Analyze queries for N+1 problems
- Add strategic caching

**Phase 3** (If still slow):
- Upgrade Render to Starter+ plan
- Add Redis caching layer
- Setup PgBouncer connection pooling

---

**Current Status**: ✅ Ready to deploy! All quick wins applied.
