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
    """Get dashboard summary with key metrics - ALL TIME TOTALS"""
    
    # Calculate total cost of units sold (COGS) - ALL TIME
    total_purchases = db.query(func.sum(SaleLineItem.cost_basis * SaleLineItem.quantity)).join(
        Sale, Sale.bill_number == SaleLineItem.bill_number
    ).filter(
        Sale.status != 'cancelled'
    ).scalar() or 0

    # Total purchase revenue - ALL TIME
    total_monthly_purchase_revenue = db.query(func.sum(PurchaseLineItem.total_price)).join(
        Purchase, Purchase.bill_number == PurchaseLineItem.bill_number
    ).filter(
        Purchase.status != 'cancelled'
    ).scalar() or 0
    
    # Calculate total sales - ALL TIME
    total_sales = db.query(func.sum(SaleLineItem.total_price)).join(
        Sale, Sale.bill_number == SaleLineItem.bill_number
    ).filter(
        Sale.status != 'cancelled'
    ).scalar() or 0
    
    # Calculate profit (only for admin) - ALL TIME
    profit = None
    if current_user.role == 'admin':
        # Get total revenue from all sales (sum of line items)
        total_sales_revenue = db.query(func.sum(SaleLineItem.total_price)).join(
            Sale, Sale.bill_number == SaleLineItem.bill_number
        ).filter(
            Sale.status != 'cancelled'
        ).scalar() or 0
        
        # Get total cost from all line items sold
        total_cost_basis = db.query(func.sum(SaleLineItem.cost_basis * SaleLineItem.quantity)).join(
            Sale, Sale.bill_number == SaleLineItem.bill_number
        ).filter(
            Sale.status != 'cancelled'
        ).scalar() or 0
        
        profit = float(total_sales_revenue or 0) - float(total_cost_basis or 0)
        
        # Ensure profit doesn't go negative unexpectedly (data quality check)
        if profit < 0:
            import logging
            logging.warning(f"Negative profit detected: {profit}. Review cost_basis calculations.")

    
    # Total stock items (current inventory)
    total_stock_items = db.query(func.count(Stock.item_id)).filter(Stock.quantity > 0).scalar() or 0
    
    # Pending payments (purchases) - ALL TIME
    pending_purchase_payments = db.query(func.sum(Purchase.total_amount - Purchase.paid_amount)).filter(
        Purchase.payment_status.in_(['pending', 'partial'])
    ).scalar() or 0
    
    # Pending payments (sales) - ALL TIME
    pending_sale_payments = db.query(func.sum(Sale.total_price - Sale.paid_amount)).filter(
        Sale.payment_status.in_(['pending', 'partial'])
    ).scalar() or 0
    
    # Recent activities
    recent_purchases = db.query(Purchase).order_by(Purchase.date.desc()).limit(5).all()
    recent_sales = db.query(Sale).order_by(Sale.date.desc()).limit(5).all()
    
    return {
        "monthly_purchases": float(total_purchases),  # This is actually COGS (all-time)
        "monthly_sales": float(total_sales),  # All-time sales
        "monthly_profit": profit,  # All-time profit
        "total_stock_items": total_stock_items,
        "pending_purchase_payments": float(pending_purchase_payments),
        "pending_sale_payments": float(pending_sale_payments),
        "recent_purchases": len(recent_purchases),
        "recent_sales": len(recent_sales),
        "total_monthly_purchase_revenue": float(total_monthly_purchase_revenue),  # All-time purchase revenue

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
        
        # Calculate purchases from line items
        purchases = db.query(func.sum(PurchaseLineItem.total_price)).join(
            Purchase, Purchase.bill_number == PurchaseLineItem.bill_number
        ).filter(
            extract('month', Purchase.date) == month,
            extract('year', Purchase.date) == year,
            Purchase.status != 'cancelled'
        ).scalar() or 0
        
        # Calculate sales from line items
        sales = db.query(func.sum(SaleLineItem.total_price)).join(
            Sale, Sale.bill_number == SaleLineItem.bill_number
        ).filter(
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
