from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.core.security import get_current_user, get_current_admin_user
from app.models.user import User
from app.models.transaction import Waste
from app.models.item import Stock
from app.models.stock_movement import StockMovement
from app.schemas.operation import WasteCreate, WasteResponse, WasteUpdate

router = APIRouter()

@router.post("/", response_model=WasteResponse, status_code=status.HTTP_201_CREATED)
async def create_waste(
    waste: WasteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record waste/damaged items sold at low price"""
    # Check that item exists in stock
    stock = db.query(Stock).filter(Stock.item_id == waste.item_id).first()
    if not stock:
        raise HTTPException(status_code=400, detail="Item not found in stock")
    
    # Calculate total
    total_price = waste.quantity * waste.price_per_unit
    
    # Create waste record
    db_waste = Waste(
        id=waste.id,
        user_id=current_user.id,
        item_id=waste.item_id,
        quantity=waste.quantity,
        price_per_unit=waste.price_per_unit,
        total_price=total_price,
        notes=waste.notes
    )
    db.add(db_waste)
    
    # Update stock
    before_qty = stock.quantity
    stock.quantity -= waste.quantity
    after_qty = stock.quantity
    
    # Record stock movement
    movement = StockMovement(
        item_id=waste.item_id,
        movement_type='waste',
        quantity_change=-waste.quantity,
        reference_id=waste.id,
        before_quantity=before_qty,
        after_quantity=after_qty,
        recorded_by=current_user.id,
        notes=f"Waste/damaged items: {waste.notes}"
    )
    db.add(movement)
    
    db.commit()
    db.refresh(db_waste)
    return db_waste

@router.get("/", response_model=List[WasteResponse])
async def get_wastes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all waste records"""
    wastes = db.query(Waste).order_by(Waste.date.desc()).offset(skip).limit(limit).all()
    return wastes

@router.get("/{waste_id}", response_model=WasteResponse)
async def get_waste(
    waste_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific waste record"""
    waste = db.query(Waste).filter(Waste.id == waste_id).first()
    if not waste:
        raise HTTPException(status_code=404, detail="Waste record not found")
    return waste

@router.put("/{waste_id}", response_model=WasteResponse)
async def update_waste(
    waste_id: str,
    waste_update: WasteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update a waste record (Admin only)"""
    waste = db.query(Waste).filter(Waste.id == waste_id).first()
    if not waste:
        raise HTTPException(status_code=404, detail="Waste record not found")
    
    update_data = waste_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(waste, field, value)
    
    # Recalculate total if quantity or price changed
    if 'quantity' in update_data or 'price_per_unit' in update_data:
        waste.total_price = waste.quantity * waste.price_per_unit
    
    db.commit()
    db.refresh(waste)
    return waste

@router.delete("/{waste_id}")
async def delete_waste(
    waste_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a waste record (Admin only)"""
    waste = db.query(Waste).filter(Waste.id == waste_id).first()
    if not waste:
        raise HTTPException(status_code=404, detail="Waste record not found")
    
    db.delete(waste)
    db.commit()
    return {"message": "Waste record deleted successfully"}
