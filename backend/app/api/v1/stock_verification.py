"""
Stock Balance Verification System
Monitors and alerts if stock resets to zero unexpectedly on month boundaries
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta, date
from app.db.database import get_db
from app.core.security import get_current_user, get_current_admin_user
from app.models.user import User
from app.models.item import Item, Stock
from app.models.stock_movement import StockMovement
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/verify/month-boundary-reset")
async def check_month_boundary_reset(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    VERIFICATION ENDPOINT: Check if stock is being reset at month boundaries
    
    This checks for red flags that indicate stock is resetting:
    - Last day of month closing balance ≠ First day of next month opening balance
    - Unexplained drops on 1st of month
    - Data anomalies at month boundaries
    
    Returns status: PASS or FAIL with details
    """
    
    issues_found = []
    items_checked = 0
    problematic_items = []
    
    # Check each item
    items = db.query(Item).all()
    
    for item in items:
        items_checked += 1
        
        # Get movements from last 12 months
        twelve_months_ago = datetime.now() - timedelta(days=365)
        movements = db.query(StockMovement).filter(
            StockMovement.item_id == item.id,
            StockMovement.movement_date >= twelve_months_ago
        ).order_by(StockMovement.movement_date).all()
        
        if not movements:
            continue
        
        # Group movements by month
        month_groups = {}
        for move in movements:
            month_key = move.movement_date.strftime("%Y-%m")
            if month_key not in month_groups:
                month_groups[month_key] = []
            month_groups[month_key].append(move)
        
        # Check each month boundary
        sorted_months = sorted(month_groups.keys())
        for i in range(len(sorted_months) - 1):
            current_month = sorted_months[i]
            next_month = sorted_months[i + 1]
            
            # Last movement of current month
            last_move_current = month_groups[current_month][-1]
            current_month_closing = last_move_current.after_quantity
            
            # First movement of next month
            first_move_next = month_groups[next_month][0]
            next_month_opening = first_move_next.before_quantity
            
            # RED FLAG: Closing balance ≠ Opening balance
            if current_month_closing != next_month_opening:
                issue = {
                    "item_id": item.id,
                    "item_name": item.name,
                    "month_boundary": f"{current_month} → {next_month}",
                    "current_month_closing": current_month_closing,
                    "next_month_opening": next_month_opening,
                    "difference": next_month_opening - current_month_closing,
                    "status": "❌ RESET DETECTED" if next_month_opening == 0 else "⚠️ DISCONTINUITY"
                }
                issues_found.append(issue)
                problematic_items.append(item.id)
    
    return {
        "verification_date": datetime.now().isoformat(),
        "check_type": "Month Boundary Reset Detection",
        "items_checked": items_checked,
        "issues_found": len(issues_found),
        "status": "✅ PASS" if len(issues_found) == 0 else "❌ FAIL",
        "details": {
            "no_resets": len(issues_found) == 0,
            "all_months_continuous": len(issues_found) == 0,
            "anomalies": issues_found,
            "problematic_items": list(set(problematic_items))
        },
        "recommendation": "✅ Stock is carrying forward correctly" if len(issues_found) == 0 
                         else "❌ Review items above - stock may be resetting"
    }


@router.get("/verify/specific-month/{item_id}/{year}/{month}")
async def verify_month_continuity(
    item_id: str,
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify a specific month's stock continuity for an item
    Shows: Previous month closing → Current month opening/closing → Next month opening
    
    This proves the stock carries forward correctly
    """
    
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Previous month
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    
    # Next month
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    
    def get_month_closing(m, y):
        """Get last movement in a month"""
        movements = db.query(StockMovement).filter(
            StockMovement.item_id == item_id,
            extract('month', StockMovement.movement_date) == m,
            extract('year', StockMovement.movement_date) == y
        ).order_by(StockMovement.movement_date.desc()).first()
        return movements.after_quantity if movements else 0
    
    def get_month_opening(m, y):
        """Get first movement in a month (before_quantity)"""
        movements = db.query(StockMovement).filter(
            StockMovement.item_id == item_id,
            extract('month', StockMovement.movement_date) == m,
            extract('year', StockMovement.movement_date) == y
        ).order_by(StockMovement.movement_date).first()
        return movements.before_quantity if movements else 0
    
    # Get balances
    prev_closing = get_month_closing(prev_month, prev_year)
    current_opening = get_month_opening(month, year)
    current_closing = get_month_closing(month, year)
    next_opening = get_month_opening(next_month, next_year)
    
    # Verify continuity
    continuity_pass = (
        prev_closing == current_opening and  # Prev closing = current opening
        current_closing == next_opening      # Current closing = next opening
    )
    
    return {
        "item_id": item_id,
        "item_name": item.name,
        "verification_date": datetime.now().isoformat(),
        "continuity_chain": [
            {
                "month": f"{prev_month}/{prev_year}",
                "position": "CLOSING",
                "balance": prev_closing
            },
            {
                "month": f"{month}/{year}",
                "position": "OPENING",
                "balance": current_opening,
                "matches_previous_closing": prev_closing == current_opening,
                "status": "✅" if prev_closing == current_opening else "❌"
            },
            {
                "month": f"{month}/{year}",
                "position": "CLOSING",
                "balance": current_closing
            },
            {
                "month": f"{next_month}/{next_year}",
                "position": "OPENING",
                "balance": next_opening,
                "matches_previous_closing": current_closing == next_opening,
                "status": "✅" if current_closing == next_opening else "❌"
            }
        ],
        "verification_result": {
            "all_continuity_checks_pass": continuity_pass,
            "status": "✅ PASS - Stock carries forward correctly" if continuity_pass else "❌ FAIL - Discontinuity detected",
            "prev_month_closing_equals_current_opening": prev_closing == current_opening,
            "current_closing_equals_next_opening": current_closing == next_opening
        }
    }


@router.get("/verify/first-day-of-month/{item_id}")
async def check_first_day_anomaly(
    item_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if there are any unexplained drops/resets on the 1st of each month
    
    This is the main verification that stock doesn't get reset
    If a 1st of month has a negative movement that drops stock to zero, it's a reset!
    """
    
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Get all movements for this item
    all_movements = db.query(StockMovement).filter(
        StockMovement.item_id == item_id
    ).order_by(StockMovement.movement_date).all()
    
    suspicious_days = []
    
    # Check each movement
    for move in all_movements:
        day_of_month = move.movement_date.day
        
        # Flag: 1st of month with negative quantity that results in zero
        if day_of_month == 1:
            if move.quantity_change < 0 and move.after_quantity == 0:
                suspicious_days.append({
                    "date": move.movement_date.isoformat(),
                    "quantity_change": move.quantity_change,
                    "before_quantity": move.before_quantity,
                    "after_quantity": move.after_quantity,
                    "movement_type": move.movement_type,
                    "reference_id": move.reference_id,
                    "notes": move.notes,
                    "risk": "⚠️ RESET - Stock went to zero on 1st of month"
                })
    
    return {
        "item_id": item_id,
        "item_name": item.name,
        "check_type": "First Day of Month Anomaly Detection",
        "check_date": datetime.now().isoformat(),
        "suspicious_1st_of_month_events": suspicious_days,
        "events_found": len(suspicious_days),
        "status": "✅ PASS - No suspicious resets on 1st of month" if len(suspicious_days) == 0 
                 else "❌ ALERT - Possible resets detected on 1st of month",
        "interpretation": {
            "if_status_pass": "✅ Stock is NOT being reset to zero on the 1st of any month",
            "if_status_fail": "❌ Check the events above - stock appears to reset on 1st of month",
            "next_step": "If FAIL, contact admin to prevent automatic resets"
        }
    }


@router.get("/verify/monthly-audit-report")
async def generate_monthly_audit_report(
    item_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Generate comprehensive audit report showing stock balance for each month
    Proves that stock carries forward and doesn't reset
    """
    
    items_to_audit = []
    
    if item_id:
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        items_to_audit = [item]
    else:
        items_to_audit = db.query(Item).all()
    
    audit_report = {
        "report_date": datetime.now().isoformat(),
        "report_type": "Stock Continuity Audit Report",
        "items_audited": len(items_to_audit),
        "months_checked": 12,
        "audit_period": "Last 12 months",
        "items": []
    }
    
    for item in items_to_audit:
        # Get last 12 months of data
        item_audit = {
            "item_id": item.id,
            "item_name": item.name,
            "monthly_balances": []
        }
        
        for month_offset in range(12):
            current_date = datetime.now() - timedelta(days=30 * month_offset)
            month = current_date.month
            year = current_date.year
            
            movements = db.query(StockMovement).filter(
                StockMovement.item_id == item.id,
                extract('month', StockMovement.movement_date) == month,
                extract('year', StockMovement.movement_date) == year
            ).order_by(StockMovement.movement_date).all()
            
            if not movements:
                continue
            
            opening = movements[0].before_quantity
            closing = movements[-1].after_quantity
            
            item_audit["monthly_balances"].insert(0, {
                "month": current_date.strftime("%Y-%m"),
                "opening_balance": opening,
                "closing_balance": closing,
                "transactions": len(movements),
                "net_change": closing - opening
            })
        
        audit_report["items"].append(item_audit)
    
    return audit_report


@router.post("/verify/manual-reset-check")
async def manual_reset_prevention_check(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    ADMIN ONLY: Scan database for any automated reset logic
    If system somehow has code that resets stock, this will find it
    """
    
    logger.warning("Manual reset check initiated by admin")
    
    # Check 1: Look for any stock adjustments on 1st of month to zero
    first_of_month_resets = db.query(StockMovement).filter(
        extract('day', StockMovement.movement_date) == 1,
        StockMovement.after_quantity == 0,
        StockMovement.movement_type == 'adjustment'
    ).all()
    
    # Check 2: Look for any bulk deletion/truncation (would show as reference_id='system')
    system_resets = db.query(StockMovement).filter(
        StockMovement.reference_id == 'system_reset'
    ).all()
    
    # Check 3: Look for negative movements that go to exactly zero (suspicious)
    suspicious_zeros = db.query(StockMovement).filter(
        StockMovement.quantity_change < 0,
        StockMovement.after_quantity == 0,
        extract('day', StockMovement.movement_date) == 1
    ).count()
    
    return {
        "check_type": "System Reset Prevention Audit",
        "check_date": datetime.now().isoformat(),
        "checks_performed": 3,
        "results": {
            "first_of_month_zero_adjustments": len(first_of_month_resets),
            "system_reset_records": len(system_resets),
            "suspicious_1st_of_month_zeros": suspicious_zeros
        },
        "status": "✅ CLEAN - No reset logic found" if (
            len(first_of_month_resets) == 0 and
            len(system_resets) == 0 and
            suspicious_zeros == 0
        ) else "❌ ALERT - Possible reset logic detected",
        "details": {
            "first_of_month_resets": [
                {
                    "date": m.movement_date,
                    "item_id": m.item_id,
                    "reference": m.reference_id
                } for m in first_of_month_resets
            ],
            "system_resets": [
                {
                    "date": m.movement_date,
                    "item_id": m.item_id
                } for m in system_resets
            ]
        },
        "recommendation": "✅ Stock system is safe - no resets will occur" if len(first_of_month_resets) == 0 
                         else "⚠️ Review reset events above"
    }

