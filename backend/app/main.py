from fastapi import FastAPI, APIRouter, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from sqlalchemy.orm import Session
import logging
import os
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="💧 Water Bottle Inventory API",
    description="Professional inventory management system for water bottle manufacturing",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS Configuration - Handle preflight and actual requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Request Timing Middleware - Log response times to identify slow endpoints
@app.middleware("http")
async def log_request_timing(request: Request, call_next):
    """Log the execution time of each request to identify bottlenecks."""
    # Skip logging for health checks and keep-alive (too noisy)
    skip_paths = {"/keep-alive", "/health"}
    if request.url.path in skip_paths:
        return await call_next(request)
    
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # Log slow requests (>1 second) or all requests if in debug mode
    if duration > 1.0:  # Only log slow requests
        logger.warning(
            f"🐌 SLOW REQUEST: {request.method} {request.url.path} "
            f"took {duration:.2f}s (status: {response.status_code})"
        )
    else:
        logger.debug(
            f"✅ {request.method} {request.url.path} "
            f"completed in {duration:.3f}s (status: {response.status_code})"
        )
    
    return response

# Basic endpoints first (don't require database)
@app.get("/")
async def root():
    return {
        "message": "💧 Water Bottle Inventory Management System",
        "status": "running",
        "timestamp": "2025-11-07",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint - doesn't require database"""
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "database_connected": os.getenv("DATABASE_URL", "NOT_SET") != "NOT_SET"
    }

@app.get("/health/db")
async def health_check_db():
    """Health check with database connection test"""
    from app.db.database import SessionLocal
    try:
        db = SessionLocal()
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
        return {
            "status": "healthy",
            "database": "connected",
            "environment": os.getenv("ENVIRONMENT", "unknown")
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@app.get("/keep-alive")
async def keep_alive():
    """Keep-alive endpoint to prevent Render from spinning down.
    Call this periodically from your frontend to keep the app running.
    No authentication required - this is just to prevent auto-shutdown.
    Recommended: Call every 5 minutes from JavaScript
    """
    return {
        "status": "alive",
        "message": "App is running. Keep calling this to prevent spin-down on Render free tier.",
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }

@app.head("/keep-alive")
async def keep_alive_head():
    """HEAD endpoint for keep-alive - even lighter than GET"""
    return

@app.get("/config")
async def config_check():
    """Debug endpoint to check configuration"""
    import os
    db_url = os.getenv("DATABASE_URL", "NOT_SET")
    return {
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "database_url_set": db_url != "NOT_SET",
        "database_url_preview": db_url[:50] + "..." if db_url != "NOT_SET" else "NOT_SET",
        "env_vars": list(os.environ.keys())[:10]  # Show first 10 env vars
    }

# API Routes - import after app setup
def setup_routes():
    try:
        from app.api.v1 import auth, purchases, sales, blows, wastes, stocks, suppliers, customers, reports, dashboard, users, extra_expenditures, invoices, stock_balance, stock_verification
        # Don't import models - they initialize when the modules are imported
        
        app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
        app.include_router(users.router, prefix="/api/v1/users", tags=["User Management"])
        app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
        app.include_router(purchases.router, prefix="/api/v1/purchases", tags=["Purchases"])
        app.include_router(sales.router, prefix="/api/v1/sales", tags=["Sales"])
        app.include_router(blows.router, prefix="/api/v1/blows", tags=["Blow Process"])
        app.include_router(wastes.router, prefix="/api/v1/wastes", tags=["Waste Management"])
        app.include_router(extra_expenditures.router, prefix="/api/v1/extra-expenditures", tags=["Extra Expenditures"])
        app.include_router(stocks.router, prefix="/api/v1/stocks", tags=["Stock & Inventory"])
        app.include_router(stock_balance.router, prefix="/api/v1/stock-balance", tags=["Stock Running Balance"])
        app.include_router(stock_verification.router, prefix="/api/v1/stock-verify", tags=["Stock Verification"])
        app.include_router(suppliers.router, prefix="/api/v1/suppliers", tags=["Suppliers"])
        app.include_router(customers.router, prefix="/api/v1/customers", tags=["Customers"])
        app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
        app.include_router(invoices.router, prefix="/api/v1/invoices", tags=["Invoice PDFs"])
        logger.info("✅ All routes loaded successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error loading routes: {e}")
        import traceback
        traceback.print_exc()
        return False

# Try to load routes on startup
routes_loaded = setup_routes()

@app.get("/debug/routes")
async def debug_routes():
    """Check which routes are registered"""
    try:
        routes = []
        for route in app.routes:
            path = getattr(route, "path", None)
            methods = getattr(route, "methods", None)
            name = getattr(route, "name", None)
            if path:
                routes.append({
                    "path": path,
                    "methods": list(methods) if methods else None,
                    "name": name
                })
        return {
            "routes_loaded_at_startup": routes_loaded,
            "route_count": len(routes),
            "auth_route_exists": any("/auth" in r.get("path", "") for r in routes),
            "sample_routes": routes[:10]
        }
    except Exception as e:
        logger.error(f"Error in debug/routes: {e}")
        return {
            "error": str(e),
            "routes_loaded_at_startup": routes_loaded
        }

@app.get("/debug/reload-routes")
async def reload_routes():
    """Force reload routes"""
    global routes_loaded
    logger.info("🔄 Attempting to reload routes...")
    routes_loaded = setup_routes()
    return {
        "routes_loaded": routes_loaded,
        "message": "Routes reloaded"
    }

# ===== SERVE REACT FRONTEND (SPA) =====
# Mount frontend dist folder to serve React app
from pathlib import Path

frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
    logger.info(f"✅ Frontend static files mounted from {frontend_dist}")
else:
    logger.warning(f"⚠️ Frontend dist folder not found at {frontend_dist}")
