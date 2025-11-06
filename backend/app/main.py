from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, purchases, sales, blows, wastes, stocks, suppliers, customers, reports, dashboard, users, extra_expenditures
from app.models import report  # Import all models to ensure they're registered

app = FastAPI(
    title="💧 Water Bottle Inventory API",
    description="Professional inventory management system for water bottle manufacturing",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS Configuration - MUST be first
origins = [
    "http://localhost:3000",   # React app
    "http://127.0.0.1:3000",   # localhost
    "http://localhost:3001",   # fallback port
    "http://127.0.0.1:3001",   # fallback port
    "http://localhost:5173",   # Vite default
    "http://127.0.0.1:5173",   # Vite default
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# API Routes
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
