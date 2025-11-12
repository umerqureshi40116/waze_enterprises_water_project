# 🚀 Performance Optimization Guide for Deployed App

## Quick Fixes Applied ✅

### 1. **Request Timing Middleware** (DONE)
**File**: `backend/app/main.py`

Added middleware to log slow requests:
```
🐌 SLOW REQUEST: GET /api/v1/sales took 5.23s (status: 200)
```

**What this does**: Automatically logs any request taking >1 second to help identify bottlenecks.

**Where to check logs**: 
- **Render Dashboard**: Go to your app → "Logs" tab
- **Look for**: Lines starting with `🐌 SLOW REQUEST`

---

### 2. **Non-Blocking PDF Generation** (DONE)
**Files**: `backend/app/api/v1/invoices.py`

Wrapped PDF generation in `asyncio.to_thread()`:
```python
# Now runs in thread pool without blocking the main event loop
pdf_buffer = await asyncio.to_thread(
    generate_sales_invoice_pdf,
    sale_bill=sale,
    customer=customer,
    line_items=line_items,
    items_db=items_list
)
```

**Impact**: PDF generation no longer blocks other requests. Your app stays responsive.

---

## Next Steps to Implement

### Step 1: Enable Query Logging (5 min)
See slow SQL queries directly:

```python
# In backend/app/db/database.py, change:
engine = create_engine(
    DATABASE_URL,
    echo=True,  # ← Add this line
    poolclass=poolclass,
    connect_args={"connect_timeout": 10, "keepalives": 1}
)
```

Then check logs for lines like:
```
SELECT users.id, users.email FROM users
```

### Step 2: Deploy & Monitor (30 min)
1. Push changes to GitHub
2. Render auto-deploys
3. Go to **Logs** tab on Render dashboard
4. Wait for requests → should see timing info

**What to look for**:
- Any endpoint taking >2 seconds?
- Same endpoint slow every time? → Query optimization needed
- Sometimes fast, sometimes slow? → Keep-alive working, or connection pooling issue

### Step 3: Quick Caching (Optional, 15 min)
If you see `/api/v1/dashboard` or `/api/v1/sales` being slow repeatedly:

```python
# Add this to reports.py
from functools import lru_cache
import time

cache_timestamps = {}

@router.get("/dashboard")
async def get_dashboard(db: Session = Depends(get_db)):
    # Cache for 5 minutes
    cache_key = "dashboard"
    now = time.time()
    
    if cache_key in cache_timestamps:
        if now - cache_timestamps[cache_key] < 300:  # 5 min
            return cached_dashboard  # Return cached data
    
    # ... fetch data ...
    cached_dashboard = result
    cache_timestamps[cache_key] = now
    return result
```

---

## Debugging Guide

### Slowness Checklist:
1. ✅ Keep-alive running? Check browser console for `✅ Keep-alive ping sent` every 10 min
2. ✅ Check Render logs for `🐌 SLOW REQUEST` messages
3. ✅ Is it the same endpoint? → Query optimization
4. ✅ Is it intermittent? → Render cold start or connection timeout
5. ✅ Multiple slow requests? → Need caching or DB upgrade

### Common Slow Endpoints:
- **`/api/v1/sales`** → Multiple queries per row. Fix: Add caching
- **`/invoices/invoice/sale/{bill_number}`** → PDF generation. Fix: Already done with `asyncio.to_thread()`
- **`/export-sales-excel`** → Large workbook generation. Fix: Can wrap in `asyncio.to_thread()`
- **`/api/v1/dashboard`** → Lots of aggregations. Fix: Cache for 5 minutes

---

## Database Connection Optimization (Already Done)

Your `backend/app/db/database.py` has:
```python
# Auto-detects Render environment
if "render.com" in DATABASE_URL:
    poolclass = NullPool  # ← Serverless-safe
else:
    poolclass = QueuePool  # ← Local with connection reuse
```

✅ This is **already optimized** for Render free tier.

---

## If Still Slow After These Fixes

### Option A: Upgrade Render Plan
- Free tier: 15 min auto-shutdown, 512MB RAM, shared CPU
- **Starter+**: Persistent, more CPU/RAM
- Check CPU usage in Render dashboard

### Option B: Add Redis Caching
```bash
# In Render dashboard, add Redis
# Then use in FastAPI:
import redis
cache = redis.Redis(url=REDIS_URL)

# Cache expensive queries for 5 minutes
@router.get("/sales")
async def get_sales():
    cached = cache.get("sales_list")
    if cached:
        return json.loads(cached)
    
    result = db.query(Sale).all()
    cache.setex("sales_list", 300, json.dumps(result))
    return result
```

### Option C: Database Connection Pool
Add **PgBouncer** (Neon has built-in):
- Go to Neon dashboard → Connection pooling → Enable
- Set pool mode to `transaction`

---

## Monitoring Template

**After deploying, check these metrics:**

| Metric | Check Where | Ideal Value |
|--------|-------------|-------------|
| Request latency | Render Logs (🐌 lines) | <500ms per request |
| Database time | SQLAlchemy logs (enable echo=True) | <100ms per query |
| Keep-alive status | Browser console | `✅ ping sent` every 10 min |
| CPU usage | Render dashboard → Metrics | <80% avg |
| Memory usage | Render dashboard → Metrics | <400MB avg |

---

## Files Modified Today

1. ✅ `backend/app/main.py` - Added request timing middleware
2. ✅ `backend/app/api/v1/invoices.py` - PDF generation now non-blocking
3. ✅ `backend/app/api/v1/reports.py` - Added asyncio import

---

## Need Help?

Run these commands to test locally:

```bash
# Terminal 1: Start backend
cd backend
python -m uvicorn app.main:app --reload --log-level debug

# Terminal 2: Test an endpoint
curl http://localhost:8000/api/v1/sales

# Watch logs for timing info and slow requests
```

Then compare with deployed version by checking Render logs.

---

**Status**: Core optimizations done. Ready to deploy and measure. 🚀
