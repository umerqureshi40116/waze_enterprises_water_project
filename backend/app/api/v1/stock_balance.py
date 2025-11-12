"""
Stock Running Balance Report - Maintains cumulative inventory across months
This module calculates opening balance, movements, and closing balance per month
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from app.db.database import get_db
from app.core.security import get_current_user, get_current_admin_user
from app.models.user import User
from app.models.item import Item, Stock
from app.models.stock_movement import StockMovement
from typing import List, Dict, Optional

router = APIRouter()


@router.get("/balance/opening-balance")
async def get_opening_balance(
    month: int = None,
    year: int = None,
    item_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get opening balance for a given month
    Opening balance = Stock at the end of previous month (cumulative)
    """
    if month is None:
        month = datetime.now().month
    if year is None:
        year = datetime.now().year
    
    # Get first day of requested month
    month_start = datetime(year, month, 1)
    
    # Get the last movement BEFORE this month started
    previous_month_end = month_start - timedelta(days=1)
    
    result = []
    
    if item_id:
        # Single item opening balance
        last_movement = db.query(StockMovement).filter(
            StockMovement.item_id == item_id,
            StockMovement.movement_date < month_start
        ).order_by(StockMovement.movement_date.desc()).first()
        
        item = db.query(Item).filter(Item.id == item_id).first()
        opening_balance = last_movement.after_quantity if last_movement else 0
        
        return {
            "item_id": item_id,
            "item_name": item.name if item else "Unknown",
            "month": f"{month}/{year}",
            "opening_balance": opening_balance
        }
    else:
        # All items opening balance
        items = db.query(Item).all()
        
        for item in items:
            last_movement = db.query(StockMovement).filter(
                StockMovement.item_id == item.id,
                StockMovement.movement_date < month_start
            ).order_by(StockMovement.movement_date.desc()).first()
            
            opening_balance = last_movement.after_quantity if last_movement else 0
            
            result.append({
                "item_id": item.id,
                "item_name": item.name,
                "opening_balance": opening_balance
            })
        
        return {
            "month": f"{month}/{year}",
            "items": result
        }


@router.get("/balance/monthly-statement")
async def get_monthly_stock_statement(
    month: int = None,
    year: int = None,
    item_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete monthly stock statement for an item or all items
    Format: Opening Balance + Movements in Month = Closing Balance
    
    This shows the running balance over time, NOT resetting each month
    """
    if month is None:
        month = datetime.now().month
    if year is None:
        year = datetime.now().year
    
    month_start = datetime(year, month, 1)
    # Get last day of month
    if month == 12:
        month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = datetime(year, month + 1, 1) - timedelta(days=1)
    
    result = []
    
    if item_id:
        # Single item statement
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Opening balance
        last_movement_before = db.query(StockMovement).filter(
            StockMovement.item_id == item_id,
            StockMovement.movement_date < month_start
        ).order_by(StockMovement.movement_date.desc()).first()
        opening_balance = last_movement_before.after_quantity if last_movement_before else 0
        
        # Movements in this month
        movements = db.query(StockMovement).filter(
            StockMovement.item_id == item_id,
            extract('month', StockMovement.movement_date) == month,
            extract('year', StockMovement.movement_date) == year
        ).order_by(StockMovement.movement_date).all()
        
        # Total movements
        total_movements = sum([m.quantity_change for m in movements])
        
        # Closing balance
        closing_balance = opening_balance + total_movements
        
        return {
            "item_id": item_id,
            "item_name": item.name,
            "month": f"{month}/{year}",
            "opening_balance": opening_balance,
            "total_inbound": sum([m.quantity_change for m in movements if m.quantity_change > 0]),
            "total_outbound": sum([m.quantity_change for m in movements if m.quantity_change < 0]),
            "total_movements": total_movements,
            "closing_balance": closing_balance,
            "movements_detail": [
                {
                    "date": m.movement_date,
                    "type": m.movement_type,
                    "quantity_change": m.quantity_change,
                    "before_quantity": m.before_quantity,
                    "after_quantity": m.after_quantity,
                    "reference_id": m.reference_id,
                    "notes": m.notes
                }
                for m in movements
            ]
        }
    else:
        # All items statement
        items = db.query(Item).all()
        
        for item in items:
            # Opening balance
            last_movement_before = db.query(StockMovement).filter(
                StockMovement.item_id == item.id,
                StockMovement.movement_date < month_start
            ).order_by(StockMovement.movement_date.desc()).first()
            opening_balance = last_movement_before.after_quantity if last_movement_before else 0
            
            # Movements in this month
            movements = db.query(StockMovement).filter(
                StockMovement.item_id == item.id,
                extract('month', StockMovement.movement_date) == month,
                extract('year', StockMovement.movement_date) == year
            ).all()
            
            total_movements = sum([m.quantity_change for m in movements])
            closing_balance = opening_balance + total_movements
            
            result.append({
                "item_id": item.id,
                "item_name": item.name,
                "opening_balance": opening_balance,
                "total_inbound": sum([m.quantity_change for m in movements if m.quantity_change > 0]),
                "total_outbound": sum([abs(m.quantity_change) for m in movements if m.quantity_change < 0]),
                "total_movements": total_movements,
                "closing_balance": closing_balance
            })
        
        return {
            "month": f"{month}/{year}",
            "statement_date": datetime.now().isoformat(),
            "items": result
        }


@router.get("/balance/cumulative-position")
async def get_cumulative_position(
    item_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get cumulative stock position from beginning of records to now
    Shows: All historical movements + Current Stock (should match)
    Proves that stock is running balance, NOT reset monthly
    """
    
    if item_id:
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # All movements (chronological order)
        movements = db.query(StockMovement).filter(
            StockMovement.item_id == item_id
        ).order_by(StockMovement.movement_date).all()
        
        # Current stock
        stock = db.query(Stock).filter(Stock.item_id == item_id).first()
        current_stock = stock.quantity if stock else 0
        
        # Total of all movements
        total_all_movements = sum([m.quantity_change for m in movements])
        
        return {
            "item_id": item_id,
            "item_name": item.name,
            "total_inbound_all_time": sum([m.quantity_change for m in movements if m.quantity_change > 0]),
            "total_outbound_all_time": sum([abs(m.quantity_change) for m in movements if m.quantity_change < 0]),
            "total_net_movements": total_all_movements,
            "current_stock": current_stock,
            "match": total_all_movements == current_stock,  # Should be True
            "movement_count": len(movements),
            "first_movement": movements[0].movement_date if movements else None,
            "last_movement": movements[-1].movement_date if movements else None
        }
    else:
        result = []
        items = db.query(Item).all()
        
        for item in items:
            movements = db.query(StockMovement).filter(
                StockMovement.item_id == item.id
            ).all()
            
            stock = db.query(Stock).filter(Stock.item_id == item.id).first()
            current_stock = stock.quantity if stock else 0
            total_movements = sum([m.quantity_change for m in movements])
            
            result.append({
                "item_id": item.id,
                "item_name": item.name,
                "total_inbound_all_time": sum([m.quantity_change for m in movements if m.quantity_change > 0]),
                "total_outbound_all_time": sum([abs(m.quantity_change) for m in movements if m.quantity_change < 0]),
                "total_net_movements": total_movements,
                "current_stock": current_stock,
                "match": total_movements == current_stock
            })
        
        return {
            "as_of": datetime.now().isoformat(),
            "items": result
        }

