from fastapi import FastAPI, APIRouter, Depends, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.core.config import settings
from sqlalchemy.orm import Session
import logging
import os
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Water Bottle Inventory API",
    description="Professional inventory management system for water bottle manufacturing",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Trust proxy headers (for Railway, Vercel, etc.)
# CRITICAL: This tells FastAPI to trust X-Forwarded-* headers from Railway's proxy
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # Railway adds proxy headers
)

# CORS Configuration - Use settings from config.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Use specific origins from config
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Middleware to preserve HTTPS protocol from Railway's proxy headers
@app.middleware("http")
async def preserve_https_protocol(request: Request, call_next):
    """
    Railway proxies requests through HTTP internally but sends X-Forwarded-Proto: https.
    This middleware ensures we respect the original protocol.
    """
    # Railway/Vercel send X-Forwarded-Proto header
    forwarded_proto = request.headers.get("x-forwarded-proto", "http")
    
    # If the original request was HTTPS (from Vercel/browser), log it
    if forwarded_proto == "https":
        logger.debug(f"✅ Original request protocol: HTTPS (via {request.headers.get('x-forwarded-host', 'unknown')})")
    
    response = await call_next(request)
    
    # Add header to response so Vercel knows we support HTTPS
    response.headers["X-Forwarded-Proto"] = forwarded_proto
    
    return response

# Middleware to ensure HTTPS is used in redirects
@app.middleware("http")
async def enforce_https_redirects(request: Request, call_next):
    """Ensure that any redirects use HTTPS protocol to prevent mixed-content errors."""
    # Process the request normally
    response = await call_next(request)
    
    # If this is a redirect response (3xx), ensure Location header uses HTTPS
    # This applies to ALL routes - including API routes - because Railway converts HTTPS to HTTP internally
    if 300 <= response.status_code < 400:
        location = response.headers.get("location")
        if location and location.startswith("http://"):
            # Railway is downgrading HTTPS→HTTP in redirects
            # Force it back to HTTPS
            original_location = location
            location = location.replace("http://", "https://")
            response.headers["location"] = location
            logger.warning(
                f"🔒 FIXED HTTPS downgrade in redirect: {original_location} → {location}"
            )
    
    return response

# Middleware to log requests and preserve HTTPS protocol
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
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import FileResponse
import mimetypes

frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"

class SPAMiddleware(BaseHTTPMiddleware):
    """Middleware to serve React app for all non-API routes"""
    async def dispatch(self, request, call_next):
        # Let routers handle API routes
        path = request.url.path
        
        # Check if it's an API route or docs
        if path.startswith("/api") or path in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Check if it's a static file
        if path.startswith("/dist/") or path.startswith("/assets/"):
            return await call_next(request)
        
        # For all other routes, check if file exists
        file_path = frontend_dist / path.lstrip("/")
        if file_path.exists() and file_path.is_file():
            # Serve the file
            return FileResponse(file_path)
        
        # If no file found, serve index.html for SPA routing
        index_file = frontend_dist / "index.html"
        if index_file.exists():
            logger.debug(f"📄 Serving index.html for SPA route: {path}")
            return FileResponse(index_file, media_type="text/html")
        
        # If index.html doesn't exist, let the request proceed (will 404)
        return await call_next(request)

# Add SPA middleware after routes are registered
# This must come AFTER API routes so they take precedence
if frontend_dist.exists():
    logger.info(f"✅ SPA middleware configured to serve from {frontend_dist}")
    app.add_middleware(SPAMiddleware)
else:
    logger.warning(f"⚠️ Frontend dist folder not found at {frontend_dist}")
