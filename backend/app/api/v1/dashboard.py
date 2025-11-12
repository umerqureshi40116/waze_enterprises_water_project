from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List
from decimal import Decimal
from datetime import datetime, timedelta
from app.db.database import get_db
from app.core.security import get_current_user
from app.core.cache import get_cache, cache_key_dashboard_summary, cache_key_monthly_stats, CACHE_TTL_DASHBOARD_SUMMARY, CACHE_TTL_MONTHLY_STATS
from app.models.user import User
from app.models.transaction import Purchase, Sale, Blow, Waste, SaleLineItem, PurchaseLineItem
from app.models.item import Stock

router = APIRouter()

@router.get("/summary")
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard summary with key metrics - OPTIMIZED with caching"""
    
    # 💾 Check cache first
    cache = get_cache()
    cache_key = cache_key_dashboard_summary(current_user.id)
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # 🚀 OPTIMIZATION: Combine all metrics into 1-2 queries instead of 8+
    
    # Query 1: Get all sales metrics for current month (combined)
    sales_metrics = db.query(
        func.sum(Sale.total_price).label('monthly_sales'),
        func.sum(SaleLineItem.cost_basis * SaleLineItem.quantity).label('cost_basis_total'),
        func.count(func.distinct(Sale.bill_number)).label('sales_count')
    ).join(
        SaleLineItem, Sale.bill_number == SaleLineItem.bill_number, isouter=True
    ).filter(
        extract('month', Sale.date) == current_month,
        extract('year', Sale.date) == current_year,
        Sale.status != 'cancelled'
    ).first()
    
    monthly_sales = float(sales_metrics.monthly_sales or 0)
    cost_basis_total = float(sales_metrics.cost_basis_total or 0)
    
    # Query 2: Get all purchase metrics for current month
    purchase_metrics = db.query(
        func.sum(Purchase.total_amount).label('monthly_purchase_revenue'),
        func.sum(Purchase.total_amount - Purchase.paid_amount).label('pending_purchase_total')
    ).filter(
        extract('month', Purchase.date) == current_month,
        extract('year', Purchase.date) == current_year,
        Purchase.status != 'cancelled'
    ).first()
    
    total_monthly_purchase_revenue = float(purchase_metrics.monthly_purchase_revenue or 0)
    
    # Query 3: Get stock and payment metrics
    stock_payment_metrics = db.query(
        func.count(func.distinct(Stock.item_id)).label('total_stock_items'),
        func.sum(Purchase.total_amount - Purchase.paid_amount).label('pending_purchase_payments'),
        func.sum(Sale.total_price - Sale.paid_amount).label('pending_sale_payments')
    ).outerjoin(
        Purchase, Purchase.payment_status.in_(['pending', 'partial'])
    ).outerjoin(
        Sale, Sale.payment_status.in_(['pending', 'partial'])
    ).filter(
        Stock.quantity > 0
    ).first()
    
    total_stock_items = stock_payment_metrics.total_stock_items or 0
    pending_purchase_payments = float(stock_payment_metrics.pending_purchase_payments or 0)
    pending_sale_payments = float(stock_payment_metrics.pending_sale_payments or 0)
    
    # Query 4: Get recent activities with only needed columns (pagination optimization)
    recent_purchases = db.query(
        Purchase.bill_number,
        Purchase.date,
        Purchase.total_amount
    ).order_by(Purchase.date.desc()).limit(5).all()
    
    recent_sales = db.query(
        Sale.bill_number,
        Sale.date,
        Sale.total_price
    ).order_by(Sale.date.desc()).limit(5).all()
    
    # Calculate profit for admin users
    profit = None
    if current_user.role == 'admin':
        profit = float(monthly_sales) - float(cost_basis_total)
        
        if profit < 0:
            import logging
            logging.warning(f"Negative profit detected for {current_month}/{current_year}: {profit}. Review cost_basis calculations.")
    
    return {
        "monthly_purchases": cost_basis_total,
        "monthly_sales": monthly_sales,
        "monthly_profit": profit,
        "total_stock_items": total_stock_items,
        "pending_purchase_payments": pending_purchase_payments,
        "pending_sale_payments": pending_sale_payments,
        "recent_purchases": len(recent_purchases),
        "recent_sales": len(recent_sales),
        "total_monthly_purchase_revenue": total_monthly_purchase_revenue,
    }
    
    # 💾 Cache the result
    result_dict = {
        "monthly_purchases": cost_basis_total,
        "monthly_sales": monthly_sales,
        "monthly_profit": profit,
        "total_stock_items": total_stock_items,
        "pending_purchase_payments": pending_purchase_payments,
        "pending_sale_payments": pending_sale_payments,
        "recent_purchases": len(recent_purchases),
        "recent_sales": len(recent_sales),
        "total_monthly_purchase_revenue": total_monthly_purchase_revenue,
    }
    cache.set(cache_key, result_dict, ttl=CACHE_TTL_DASHBOARD_SUMMARY)
    return result_dict

@router.get("/stats/monthly")
async def get_monthly_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get monthly statistics for charts - OPTIMIZED with single query and caching"""
    
    # 💾 Check cache first
    cache = get_cache()
    cache_key = cache_key_monthly_stats(current_user.id)
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    # 🚀 OPTIMIZATION: Instead of looping 6 times with 2 queries each (12 queries),
    # use a single query with GROUP BY to get all 6 months data at once!
    
    from sqlalchemy.sql import label
    
    # Get all monthly data in ONE query
    monthly_results = db.query(
        extract('year', Purchase.date).label('year'),
        extract('month', Purchase.date).label('month'),
        func.sum(Purchase.total_amount).label('purchases'),
        func.sum(Sale.total_price).label('sales')
    ).outerjoin(
        Sale, (extract('year', Purchase.date) == extract('year', Sale.date)) &
              (extract('month', Purchase.date) == extract('month', Sale.date))
    ).filter(
        Purchase.date >= datetime.now() - timedelta(days=180),  # Last 6 months
        Purchase.status != 'cancelled'
    ).group_by(
        extract('year', Purchase.date),
        extract('month', Purchase.date)
    ).order_by(
        extract('year', Purchase.date).asc(),
        extract('month', Purchase.date).asc()
    ).all()
    
    # If no purchase data, get sales data for last 6 months
    if not monthly_results:
        monthly_results = db.query(
            extract('year', Sale.date).label('year'),
            extract('month', Sale.date).label('month'),
            func.cast(0, db.Numeric).label('purchases'),
            func.sum(Sale.total_price).label('sales')
        ).filter(
            Sale.date >= datetime.now() - timedelta(days=180),
            Sale.status != 'cancelled'
        ).group_by(
            extract('year', Sale.date),
            extract('month', Sale.date)
        ).order_by(
            extract('year', Sale.date).asc(),
            extract('month', Sale.date).asc()
        ).all()
    
    # Format results
    monthly_data = []
    for result in monthly_results:
        month_num = int(result.month) if result.month else 1
        year_num = int(result.year) if result.year else datetime.now().year
        
        try:
            month_date = datetime(year_num, month_num, 1)
            month_str = month_date.strftime("%b %Y")
        except:
            month_str = f"Month {month_num}/{year_num}"
        
        monthly_data.append({
            "month": month_str,
            "purchases": float(result.purchases or 0),
            "sales": float(result.sales or 0)
        })
    
    # If we got less than 6 months, pad with zeros
    if len(monthly_data) < 6:
        for i in range(6 - len(monthly_data)):
            past_date = datetime.now() - timedelta(days=30 * (6 - i))
            monthly_data.insert(0, {
                "month": past_date.strftime("%b %Y"),
                "purchases": 0,
                "sales": 0
            })
    
    result = monthly_data[-6:]  # Get last 6 months
    
    # 💾 Cache the result
    cache.set(cache_key, result, ttl=CACHE_TTL_MONTHLY_STATS)
    return result
