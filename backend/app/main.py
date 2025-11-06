from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
import logging

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

# Basic endpoints first (don't require database)
@app.get("/")
async def root():
    return {
        "message": "💧 Water Bottle Inventory Management System",
        "status": "running",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

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
        from app.api.v1 import auth, purchases, sales, blows, wastes, stocks, suppliers, customers, reports, dashboard, users, extra_expenditures
        from app.models import report
        
        app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
        app.include_router(users.router, prefix="/api/v1/users", tags=["User Management"])
        app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
        app.include_router(purchases.router, prefix="/api/v1/purchases", tags=["Purchases"])
        app.include_router(sales.router, prefix="/api/v1/sales", tags=["Sales"])
        app.include_router(blows.router, prefix="/api/v1/blows", tags=["Blow Process"])
        app.include_router(wastes.router, prefix="/api/v1/wastes", tags=["Waste Management"])
        app.include_router(extra_expenditures.router, prefix="/api/v1/extra-expenditures", tags=["Extra Expenditures"])
        app.include_router(stocks.router, prefix="/api/v1/stocks", tags=["Stock & Inventory"])
        app.include_router(suppliers.router, prefix="/api/v1/suppliers", tags=["Suppliers"])
        app.include_router(customers.router, prefix="/api/v1/customers", tags=["Customers"])
        app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
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
