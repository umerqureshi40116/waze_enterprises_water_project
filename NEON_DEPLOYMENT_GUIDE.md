# Neon + Render Deployment Guide

Complete guide to deploy your Water App with **Neon PostgreSQL** (free) and **Render** (free tier).

---

## Architecture Overview

```
┌─────────────────────┐
│   Your Computer     │
│  (Local Dev)        │
└──────────┬──────────┘
           │ git push
           ▼
┌─────────────────────┐
│   GitHub            │
│  (Code Repository)  │
└──────────┬──────────┘
           │ auto-deploy on push
           ├─────────────────┬──────────────────┐
           ▼                 ▼                  ▼
    ┌─────────────┐   ┌──────────────┐   ┌──────────────┐
    │   Render    │   │    Neon      │   │   Render     │
    │   Backend   │◄──┤ PostgreSQL   │   │  Frontend    │
    │   (FastAPI) │   │  Database    │   │  (Static)    │
    └─────────────┘   └──────────────┘   └──────────────┘
           │                                    │
           ├────────────────┬───────────────────┤
           │                │                   │
           ▼                ▼                   ▼
       Users Access via: https://your-app-name.onrender.com
```

---

## Step 1: Create Neon PostgreSQL Database (FREE)

### 1.1 Sign Up
1. Go to https://console.neon.tech/signup
2. Click **"Sign up with GitHub"** (easiest option)
3. Authorize Neon to access your GitHub account
4. Confirm your email

### 1.2 Create New Project
1. Click **"New Project"** button
2. **Project Name**: `water-app`
3. **Region**: Select closest to your users (e.g., US East if in Pakistan, use Europe)
4. **Postgres Version**: Keep default (16+)
5. Click **"Create Project"**

### 1.3 Get Connection String
1. After project creates, you'll see a connection string like:
   ```
   postgresql://neondb_owner:abcd1234@ep-xyz.us-east-1.neon.tech/neondb
   ```
2. **Copy this** - you'll need it for backend

### 1.4 Important Settings
- Click **Settings** tab
- Under **Database**, set:
  - Auto-suspend: After 5 minutes (saves compute)
  - Max autoscale: 1 CU (prevents runaway costs)

---

## Step 2: Deploy Backend to Render

### 2.1 Prepare Your Backend

Update your `.env` file in `backend/.env`:

```env
# Replace with your Neon connection string
DATABASE_URL=postgresql://neondb_owner:your_password@ep-xyz.us-east-1.neon.tech/neondb

# Keep these the same
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 2.2 Create backend/.env.example (for Git)

Create `backend/.env.example` to show what env vars are needed:

```env
DATABASE_URL=postgresql://username:password@host:5432/dbname
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 2.3 Sign Up to Render

1. Go to https://render.com
2. Click **"Sign up with GitHub"**
3. Authorize Render to access your GitHub
4. Confirm email

### 2.4 Create Backend Service

1. From Render dashboard, click **"New +"** → **"Web Service"**
2. Connect to your GitHub repository:
   - Search: `waze_enterprises_water_project`
   - Click **"Connect"**
3. Configure the service:

| Setting | Value |
|---------|-------|
| **Name** | `water-app-backend` |
| **Region** | `Oregon (US West)` or closest |
| **Branch** | `master` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r backend/requirements.txt` |
| **Start Command** | `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000` |

4. Click **"Create Web Service"**

### 2.5 Add Environment Variables

In the Render dashboard for your backend service:

1. Click **"Environment"** tab
2. Click **"Add Environment Variable"**
3. Add each variable:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | Your Neon connection string |
| `SECRET_KEY` | A secure random string (or use existing) |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |

4. Click **"Save Changes"**
5. Render will **automatically redeploy** with new vars

### 2.6 Wait for Backend Deployment

- Render builds and deploys (takes 5-10 minutes)
- You'll see status: **"Live"** when ready
- Your backend URL: `https://water-app-backend.onrender.com`
- Test it: Visit `https://water-app-backend.onrender.com/api/v1/docs` - should see Swagger UI

---

## Step 3: Deploy Frontend to Render

### 3.1 Update Frontend API URL

In `frontend/src/api/axios.js`, update the API base URL:

```javascript
const API_BASE_URL = process.env.VITE_API_URL || 'https://water-app-backend.onrender.com';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

export default api;
```

Create `frontend/.env.production`:

```env
VITE_API_URL=https://water-app-backend.onrender.com
```

### 3.2 Push Changes to GitHub

```bash
cd e:\water
git add .
git commit -m "Update API URL for production deployment"
git push origin master
```

### 3.3 Create Frontend Service in Render

1. From Render dashboard, click **"New +"** → **"Static Site"**
2. Connect to your GitHub repository (same one)
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `water-app-frontend` |
| **Region** | Same as backend (Oregon) |
| **Branch** | `master` |
| **Build Command** | `cd frontend && npm install && npm run build` |
| **Publish Directory** | `frontend/dist` |

4. Click **"Create Static Site"**

### 3.4 Add Frontend Environment Variables

1. Click **"Environment"** tab
2. Add:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://water-app-backend.onrender.com` |

3. Render will redeploy automatically (2-3 minutes)

### 3.5 Access Your Application

- Your frontend URL: `https://water-app-frontend.onrender.com`
- Login page will load automatically
- Use your credentials to log in

---

## Step 4: Verify Everything Works

### 4.1 Test Backend

```bash
curl https://water-app-backend.onrender.com/api/v1/docs
```

Should return Swagger UI documentation.

### 4.2 Test Frontend

1. Visit: `https://water-app-frontend.onrender.com`
2. Login with test credentials (Waheed/Zeeshan or test user)
3. Try creating a sample transaction:
   - Go to **Sales** → Add new sale
   - Fill in details
   - Submit

### 4.3 Test Database Connection

1. Create a sale or purchase
2. Go to **Reports** → Download Daily Report
3. Should generate Excel file with your transaction

---

## Step 5: Important Notes

### Cold Starts (First Request Takes Longer)

- Neon database scales to zero after 5 minutes of inactivity
- First request after inactivity = ~5-10 second delay (normal!)
- Subsequent requests = instant

### Scaling Limits (For 5 Users)

Your free tier can handle:
- ✅ Up to 50-100 concurrent users
- ✅ ~1000 transactions per day
- ✅ Large Excel exports (< 100MB)
- No performance issues expected

### Monitoring

**Check Backend Status:**
- Render Dashboard → `water-app-backend` → **Logs** tab
- See real-time errors and API calls

**Check Database Health:**
- Neon Console → Your project → **Monitoring** tab
- See CPU, memory, connections

### Automatic Redeployment

Every time you push to GitHub:
1. Render automatically detects changes
2. Rebuilds your app
3. Deploys new version (0 downtime)
4. No manual deployment needed!

---

## Step 6: Add Custom Domain (Optional Later)

Once app is stable, add a custom domain:

1. **For Backend:**
   - Render → Backend Service → Settings → Custom Domain
   - Example: `api.yourcompany.com`

2. **For Frontend:**
   - Render → Frontend Site → Settings → Custom Domain
   - Example: `app.yourcompany.com`

3. Update DNS records with your domain provider

---

## Troubleshooting

### Backend Won't Deploy

**Error in Render logs:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
- Update `backend/requirements.txt` to include all dependencies
- Push to GitHub
- Render redeploys automatically

### Frontend Shows "Cannot Connect to API"

**Causes:**
1. Wrong API URL in `frontend/.env.production`
2. Backend not running
3. CORS issues

**Solutions:**
1. Verify API URL: `https://water-app-backend.onrender.com`
2. Check Render → Backend Service → Logs
3. Ensure backend `main.py` has CORS enabled:
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

### Database Connection Timeout

**Error:**
```
FATAL: remaining connection slots are reserved for non-replication superuser connections
```

**Solution:**
- Go to Neon Console
- Settings → Max connections
- Increase to 100+ (for Launch plan, this costs ~$2/month)

### Slow Reports Generation

**Cause:** Database scaling down after inactivity

**Solution:**
- First request wakes up database (~5-10 seconds)
- Subsequent requests are instant
- This is normal and expected

---

## Cost Breakdown (Monthly)

| Service | Cost | Notes |
|---------|------|-------|
| **Neon PostgreSQL** | $0 | Free tier (0.5GB, 100 CU-hours) |
| **Render Backend** | $0 | Free tier (750 hours/month) |
| **Render Frontend** | $0 | Free tier (unlimited static) |
| **Total** | **$0/month** | ✅ Completely free! |

**If you exceed free tier:**
- Neon: $6/month Basic plan
- Render: $7/month for backend, $0.20/GB for frontend
- Unlikely for < 5 users

---

## Next Steps

1. ✅ Create Neon database (Step 1)
2. ✅ Deploy backend (Step 2)
3. ✅ Deploy frontend (Step 3)
4. ✅ Verify everything (Step 4)
5. Share `https://water-app-frontend.onrender.com` with your 5 users
6. Monitor Render and Neon dashboards for any issues

---

## Support

- **Render Issues:** support@render.com or Render community
- **Neon Issues:** support@neon.tech or their docs
- **Your App Issues:** Check logs in both dashboards

Happy deploying! 🚀
