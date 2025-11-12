from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List
from decimal import Decimal
from datetime import datetime, timedelta
from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.transaction import Purchase, Sale, Blow, Waste, SaleLineItem, PurchaseLineItem
from app.models.item import Stock

router = APIRouter()

@router.get("/summary")
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard summary with key metrics"""
    
    try:
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Simple, safe queries - one at a time
        
        # Query 1: Monthly sales
        monthly_sales = db.query(func.sum(Sale.total_price)).filter(
            extract('month', Sale.date) == current_month,
            extract('year', Sale.date) == current_year,
            Sale.status != 'cancelled'
        ).scalar() or 0
        
        # Query 2: Cost basis total from sale line items
        cost_basis_total = db.query(func.sum(SaleLineItem.cost_basis * SaleLineItem.quantity)).filter(
            extract('month', SaleLineItem.created_at) == current_month,
            extract('year', SaleLineItem.created_at) == current_year,
        ).scalar() or 0
        
        # Query 3: Purchase revenue
        total_monthly_purchase_revenue = db.query(func.sum(Purchase.total_amount)).filter(
            extract('month', Purchase.date) == current_month,
            extract('year', Purchase.date) == current_year,
            Purchase.status != 'cancelled'
        ).scalar() or 0
        
        # Query 4: Stock count
        total_stock_items = db.query(func.count(Stock.item_id)).filter(
            Stock.quantity > 0
        ).scalar() or 0
        
        # Query 5: Pending purchase payments
        pending_purchase_payments = db.query(func.sum(Purchase.total_amount - Purchase.paid_amount)).filter(
            Purchase.payment_status.in_(['pending', 'partial'])
        ).scalar() or 0
        
        # Query 6: Pending sale payments
        pending_sale_payments = db.query(func.sum(Sale.total_price - Sale.paid_amount)).filter(
            Sale.payment_status.in_(['pending', 'partial'])
        ).scalar() or 0
        
        # Query 7-8: Recent activities
        recent_purchases_count = db.query(func.count(Purchase.bill_number)).limit(5).scalar() or 0
        recent_sales_count = db.query(func.count(Sale.bill_number)).limit(5).scalar() or 0
        
        # Calculate profit for admin users
        profit = None
        if current_user.role == 'admin':
            profit = float(monthly_sales or 0) - float(cost_basis_total or 0)
        
        # Return result
        return {
            "monthly_purchases": float(cost_basis_total or 0),
            "monthly_sales": float(monthly_sales or 0),
            "monthly_profit": profit,
            "total_stock_items": total_stock_items or 0,
            "pending_purchase_payments": float(pending_purchase_payments or 0),
            "pending_sale_payments": float(pending_sale_payments or 0),
            "recent_purchases": recent_purchases_count,
            "recent_sales": recent_sales_count,
            "total_monthly_purchase_revenue": float(total_monthly_purchase_revenue or 0),
        }
        
    except Exception as e:
        import logging
        logging.error(f"Dashboard summary error: {str(e)}", exc_info=True)
        return {
            "error": str(e),
            "monthly_purchases": 0,
            "monthly_sales": 0,
            "monthly_profit": None,
            "total_stock_items": 0,
        }

@router.get("/stats/monthly")
async def get_monthly_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get monthly statistics for charts"""
    
    try:
        # Get last 6 months of data with simple, safe queries
        monthly_data = []
        for i in range(6):
            date = datetime.now() - timedelta(days=30*i)
            month = date.month
            year = date.year
            
            # Query purchases for this month
            purchases = db.query(func.sum(Purchase.total_amount)).filter(
                extract('month', Purchase.date) == month,
                extract('year', Purchase.date) == year,
                Purchase.status != 'cancelled'
            ).scalar() or 0
            
            # Query sales for this month
            sales = db.query(func.sum(Sale.total_price)).filter(
                extract('month', Sale.date) == month,
                extract('year', Sale.date) == year,
                Sale.status != 'cancelled'
            ).scalar() or 0
            
            monthly_data.insert(0, {
                "month": date.strftime("%b %Y"),
                "purchases": float(purchases or 0),
                "sales": float(sales or 0)
            })
        
        return monthly_data
        
    except Exception as e:
        import logging
        logging.error(f"Monthly stats error: {str(e)}", exc_info=True)
        return []
