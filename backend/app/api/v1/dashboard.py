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
    
    # Calculate total purchases this month
    current_month = datetime.now().month
    current_year = datetime.now().year
    


    # Monthly cost of units sold (from sales - sum of line item costs)
    monthly_purchases = db.query(func.sum(SaleLineItem.cost_basis * SaleLineItem.quantity)).join(
        Sale, Sale.bill_number == SaleLineItem.bill_number
    ).filter(
        extract('month', Sale.date) == current_month,
        extract('year', Sale.date) == current_year,
        Sale.status != 'cancelled'
    ).scalar() or 0


    # Total monthly purchase revenue (from purchases)
    total_monthly_purchase_revenue = db.query(func.sum(Purchase.total_amount)).filter(
        extract('month', Purchase.date) == current_month,
        extract('year', Purchase.date) == current_year,
        Purchase.status != 'cancelled'
    ).scalar() or 0
    
    # Calculate total sales this month
    monthly_sales = db.query(func.sum(Sale.total_price)).filter(
        extract('month', Sale.date) == current_month,
        extract('year', Sale.date) == current_year,
        Sale.status != 'cancelled'
    ).scalar() or 0
    
    # Calculate profit (only for admin)
    profit = None
    if current_user.role == 'admin':
        # Get total revenue from sales this month
        total_sales_revenue = db.query(func.sum(Sale.total_price)).filter(
            extract('month', Sale.date) == current_month,
            extract('year', Sale.date) == current_year,
            Sale.status != 'cancelled'
        ).scalar() or 0
        
        # Get total cost from all line items sold this month
        total_cost_basis = db.query(func.sum(SaleLineItem.cost_basis * SaleLineItem.quantity)).join(
            Sale, Sale.bill_number == SaleLineItem.bill_number
        ).filter(
            extract('month', Sale.date) == current_month,
            extract('year', Sale.date) == current_year,
            Sale.status != 'cancelled'
        ).scalar() or 0
        
        profit = float(total_sales_revenue or 0) - float(total_cost_basis or 0)
        
        # Ensure profit doesn't go negative unexpectedly (data quality check)
        if profit < 0:
            import logging
            logging.warning(f"Negative profit detected for {current_month}/{current_year}: {profit}. Review cost_basis calculations.")

    
    # Total stock value
    total_stock_items = db.query(func.count(Stock.item_id)).filter(Stock.quantity > 0).scalar() or 0
    
    # Pending payments (purchases)
    pending_purchase_payments = db.query(func.sum(Purchase.total_amount - Purchase.paid_amount)).filter(
        Purchase.payment_status.in_(['pending', 'partial'])
    ).scalar() or 0
    
    # Pending payments (sales)
    pending_sale_payments = db.query(func.sum(Sale.total_price - Sale.paid_amount)).filter(
        Sale.payment_status.in_(['pending', 'partial'])
    ).scalar() or 0
    
    # Recent activities
    recent_purchases = db.query(Purchase).order_by(Purchase.date.desc()).limit(5).all()
    recent_sales = db.query(Sale).order_by(Sale.date.desc()).limit(5).all()
    
    return {
        "monthly_purchases": float(monthly_purchases),
        "monthly_sales": float(monthly_sales),
        "monthly_profit": profit,
        "total_stock_items": total_stock_items,
        "pending_purchase_payments": float(pending_purchase_payments),
        "pending_sale_payments": float(pending_sale_payments),
        "recent_purchases": len(recent_purchases),
        "recent_sales": len(recent_sales),
        "total_monthly_purchase_revenue": float(total_monthly_purchase_revenue),
    }

@router.get("/stats/monthly")
async def get_monthly_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get monthly statistics for charts"""
    
    # Get last 6 months data
    monthly_data = []
    for i in range(6):
        date = datetime.now() - timedelta(days=30*i)
        month = date.month
        year = date.year
        
        purchases = db.query(func.sum(Purchase.total_amount)).filter(
            extract('month', Purchase.date) == month,
            extract('year', Purchase.date) == year,
            Purchase.status != 'cancelled'
        ).scalar() or 0
        
        sales = db.query(func.sum(Sale.total_price)).filter(
            extract('month', Sale.date) == month,
            extract('year', Sale.date) == year,
            Sale.status != 'cancelled'
        ).scalar() or 0
        
        monthly_data.insert(0, {
            "month": date.strftime("%b %Y"),
            "purchases": float(purchases),
            "sales": float(sales)
        })
    
    return monthly_data
