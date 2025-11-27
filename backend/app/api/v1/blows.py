from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.core.security import get_current_user, get_current_admin_user
from app.models.user import User
from app.models.transaction import Blow, Purchase
from app.models.item import Item, Stock
from sqlalchemy import func
from app.models.stock_movement import StockMovement
from app.schemas.operation import BlowCreate, BlowResponse, BlowUpdate

router = APIRouter()

@router.post("/", response_model=BlowResponse, status_code=status.HTTP_201_CREATED)
async def create_blow_process(
    blow: BlowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new blow process (convert preform to bottle)"""
    # Check that preform item exists
    from_item = db.query(Item).filter(Item.id == blow.from_item_id).first()
    if not from_item:
        raise HTTPException(status_code=400, detail="Preform item not found")
    
    # Check that preform has stock
    from_stock = db.query(Stock).filter(Stock.item_id == blow.from_item_id).first()
    if not from_stock:
        raise HTTPException(status_code=400, detail="Preform item not found in stock")
    
    # ✅ ALLOW NEGATIVE STOCK: Removed insufficent stock check - stock can go into minus
    # if from_stock.quantity < blow.input_quantity:
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f"Insufficient preform stock. Required: {blow.input_quantity}, Available: {from_stock.quantity}"
    #     )
    
    # Auto-determine to_item_id if not provided (find bottle with matching size and grade)
    if not blow.to_item_id:
        to_item = db.query(Item).filter(
            Item.type == 'bottle',
            Item.size == from_item.size,
            Item.grade == from_item.grade
        ).first()
        if not to_item:
            raise HTTPException(
                status_code=400,
                detail=f"No matching bottle found for preform size {from_item.size} grade {from_item.grade}"
            )
        blow.to_item_id = to_item.id
    else:
        # Validate the to_item exists if provided
        to_item = db.query(Item).filter(Item.id == blow.to_item_id).first()
        if not to_item:
            raise HTTPException(status_code=400, detail="Target item not found")
        # Allow any item type to be produced (not just bottles)
    
    # Calculate output and waste
    # Assuming 95% efficiency by default, can be adjusted
    output_quantity = int(blow.input_quantity * 0.95)
    waste_quantity = blow.input_quantity - output_quantity
    
    # ✅ FIXED: Prevent division by zero for efficiency rate
    if blow.input_quantity <= 0:
        raise HTTPException(
            status_code=400, 
            detail="Input quantity must be greater than 0"
        )
    
    efficiency_rate = (output_quantity / blow.input_quantity) * 100
    
    # ✅ FIXED: Validate that waste is never negative
    if waste_quantity < 0:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid calculation: waste quantity cannot be negative. Input: {blow.input_quantity}, Output: {output_quantity}"
        )
    
    # Create blow record
    db_blow = Blow(
        id=blow.id,
        user_id=current_user.id,
        from_item_id=blow.from_item_id,
        to_item_id=blow.to_item_id,
        quantity=output_quantity,
        blow_cost_per_unit=blow.blow_cost_per_unit,
        produced_unit_cost=None,
        input_quantity=blow.input_quantity,
        output_quantity=output_quantity,
        waste_quantity=waste_quantity,
        efficiency_rate=efficiency_rate,
        notes=blow.notes
    )
    db.add(db_blow)
    
    # Update from_item stock (reduce preforms)
    before_from = from_stock.quantity
    from_stock.quantity -= blow.input_quantity
    after_from = from_stock.quantity
    
    # Record stock movement for preform consumption
    movement_from = StockMovement(
        item_id=blow.from_item_id,
        movement_type='production',
        quantity_change=-blow.input_quantity,
        reference_id=blow.id,
        before_quantity=before_from,
        after_quantity=after_from,
        recorded_by=current_user.id,
        notes=f"Preform used in blow process"
    )
    db.add(movement_from)
    
    # Update to_item stock (increase bottles)
    to_stock = db.query(Stock).filter(Stock.item_id == blow.to_item_id).first()
    if to_stock:
        before_to = to_stock.quantity
        to_stock.quantity += output_quantity
        after_to = to_stock.quantity
    else:
        before_to = 0
        to_stock = Stock(item_id=blow.to_item_id, quantity=output_quantity)
        db.add(to_stock)
        after_to = output_quantity
    
    # Record stock movement for bottle production
    movement_to = StockMovement(
        item_id=blow.to_item_id,
        movement_type='production',
        quantity_change=output_quantity,
        reference_id=blow.id,
        before_quantity=before_to,
        after_quantity=after_to,
        recorded_by=current_user.id,
        notes=f"Bottles produced from blow process"
    )
    db.add(movement_to)
    
    # Attempt to compute produced_unit_cost: last preform purchase price at or before now
    try:
        preform_purchase = db.query(Purchase).filter(Purchase.item_id == blow.from_item_id, Purchase.date <= func.now()).order_by(Purchase.date.desc()).first()
        if preform_purchase and preform_purchase.unit_price is not None:
            preform_price = float(preform_purchase.unit_price)
            blow_cost_unit = float(blow.blow_cost_per_unit or 0)
            db_blow.produced_unit_cost = preform_price + blow_cost_unit
    except Exception:
        # if anything fails, leave produced_unit_cost as None
        pass

    db.commit()
    db.refresh(db_blow)
    return db_blow

@router.get("/", response_model=List[BlowResponse])
async def get_blow_processes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all blow processes"""
    blows = db.query(Blow).order_by(Blow.date_time.desc()).offset(skip).limit(limit).all()
    return blows

@router.get("/{blow_id}", response_model=BlowResponse)
async def get_blow_process(
    blow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific blow process"""
    blow = db.query(Blow).filter(Blow.id == blow_id).first()
    if not blow:
        raise HTTPException(status_code=404, detail="Blow process not found")
    return blow

@router.put("/{blow_id}", response_model=BlowResponse)
async def update_blow_process(
    blow_id: str,
    blow_update: BlowUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Update a blow process (Admin only)"""
    blow = db.query(Blow).filter(Blow.id == blow_id).first()
    if not blow:
        raise HTTPException(status_code=404, detail="Blow process not found")
    
    update_data = blow_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(blow, field, value)
    
    db.commit()
    db.refresh(blow)
    return blow

@router.delete("/{blow_id}")
async def delete_blow_process(
    blow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Delete a blow process (Admin only)"""
    blow = db.query(Blow).filter(Blow.id == blow_id).first()
    if not blow:
        raise HTTPException(status_code=404, detail="Blow process not found")
    
    db.delete(blow)
    db.commit()
    return {"message": "Blow process deleted successfully"}
